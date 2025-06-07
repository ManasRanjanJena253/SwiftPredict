# Importing dependencies
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.model_selection import train_test_split, cross_validate
from imblearn.over_sampling import SMOTE
from client.swift_predict import SwiftPredict
from statistics import multimode
import pandas as pd
import numpy as np


def get_dtype_columns(df):
    """
    Gives all the columns segregated on the basis of their dtypes.
    :param df: The pandas dataframe of the dataset.
    :return: A dictionary containing the dtype as key and the list of columns of that dtype as values.
    """
    cat_columns = df.select_dtypes(include = ["object"]).columns.tolist()
    num_columns = df.select_dtypes(include = ["int64", "int32", "float64", "float32"]).columns.tolist()
    date_columns = df.select_dtypes(include = ["datetime64[ns]"]).columns.tolist()
    bool_columns = df.select_dtypes(include = ["bool"]).columns.tolist()

    return {"categorical": cat_columns, "numeric": num_columns, "date": date_columns, "bool": bool_columns}

def handle_null_values(df):
    """
    Handles the null values in a dataset.
    :param df: The dataset in the format of pandas dataframe.
    :return: A pandas dataframe after all null value issues have been resolved.
    """
    total_null_rows = df.isnull().any(axis = 1).sum()   # Will give the total no. of rows having null values.
    total_rows = df.any(axis = 1).sum()   # Gives the total no. of rows in the data.

    if total_null_rows:    # Checking if there are any null values or not.

         # Dropping the data if it's less than a threshold i.e. less that 10% of total data.
        if total_null_rows <= (0.1 * total_rows):
            df.dropna(inplace = True)
            return df
        else:
            columns = get_dtype_columns(df = df)
            null_columns = df.columns[df.isnull().any(axis=0)].tolist()  # This will give all the null columns
            cat_columns = columns["categorical"]
            bool_columns = columns["bool"]
            num_columns = columns["numeric"]

            for k in null_columns:
                if k in cat_columns or bool_columns:
                    df[k] = df[k].fillna(value = df[k].mode()[0])

                elif k in num_columns:
                    df[k] = df[k].fillna(value = df[k].mean()[0])

                else :
                    df[k] = df[k].interpolate(method = "time")

    else:
        return df

def detect_task(df, y: str):
    """
    Takes in the dataset df and the target label and finds what kind of task is to be performed on the dataset.
    i.e. Classification or Regression
    :param df: The pandas dataframe of the dataset.
    :param y: The target label.
    :return: The type task to be done. Either "classification" or "regression"
    """
    df = df
    target = df[y]

    if target.dtype == "object" or target.dtype.name == "category":
        return "classification"

    elif np.issubdtype(target.dtype, np.integer):   # Checking if the dtype of target lies in subcategory of all the integers such as int32, int64 e.t.c.
        if target.nunique() <= 20:    # If the uniques classes is > 20, then assume that the task is regression.
            return "classification"
        else:
            return "regression"

    elif np.issubdtype(target.dtype, np.floating):
        return "regression"

def handle_imbalance(df, target_column : str, X_train, y_train):
    """
    Used to fisx imbalanced dataset.
    :param df: The pandas dataframe of the dataset
    :param target_column: The name of the target column
    :param X_train: The training features after train_test_split
    :param y_train: The target features after train test split.
    :return: X_res and y_res.
    """
    target = df[target_column]
    class_counts = target.value_counts().tolist()
    max_data = class_counts.max()
    min_data = class_counts.min()

    if min_data/max_data >= 0.15:  # If the min data is less than 15 % of the max data the dataset will be considered imbalanced.
        smote = SMOTE(random_state = 21)
        X_res, target_res = smote.fit_resample(X_train, y_train)

        return X_res, target_res

    else:
        return X_train, y_train

def model_zoo(task, model = None):
    """
    Gives the models required for a specific task.
    :param task: The task to be performed on the dataset.
    :param model: Any optional model if required specifically. OPTIONAL.
    :return: List of models.
    """
    if task == "classification":
        models = [GaussianNB, XGBClassifier, RandomForestClassifier, LGBMClassifier, LogisticRegression]
        if model:
            return models.append(model)
        else:
            return models
    else:
        models = [LinearRegression, XGBRegressor, LGBMRegressor, RandomForestRegressor]
        if model:
            return models.append(model)
        else:
            return models

def train_model(task, X_train, y_train, logger):
    """
    Used to train the models and log the model results.
    :param task: The type of task to be performed on the dataset.
    :param X_train: The training features.
    :param y_train: The training labels.
    :param logger: The class used for logging the data.
    :return: Best Model
    """
    if task == "classification":
        avg_acc_scores = []
        avg_f1_score = []
        avg_precision = []
        avg_roc = []
        models = model_zoo(task = task)
        trained_models = {}
        scoring_methods = ["accuracy", "f1", "roc_auc", "precision"]
        for k in models:   # Training each classification model in model zoo.
            model = k()
            cv = cross_validate(estimator = model, X = X_train, y = y_train, cv = 10, scoring = scoring_methods)
            acc = cv["test_accuracy"]
            f1 = cv["test_f1"]
            roc = cv["test_roc_auc"]
            precision = cv["test_precision"]
            trained_models[str(k)] = model.fit(X_train, y_train)
            logger.log_params(model.get_params())

            for step in range(len(acc)):
                logger.log_metric(step = step, value = acc[step], key = "accuracy")
                logger.log_metric(step = step, value = f1[step], key = "f1_score")
                logger.log_metric(step = step, value = roc[step], key = "roc_auc")
                logger.log_metric(step = step, value = precision[step], key = "precision")

            avg_roc.append(roc.mean())
            avg_precision.append(precision.mean())
            avg_f1_score.append(f1.mean())
            avg_acc_scores.append(acc.mean())

        performers = [
            avg_acc_scores.index(max(avg_acc_scores)),
            avg_f1_score.index(max(avg_f1_score)),
            avg_roc.index(max(avg_roc)),
            avg_precision.index(max(avg_precision))
            ]

        overall_best = multimode(performers)

        best_models = {"f1": trained_models[
            str(models[avg_f1_score.index(max(avg_f1_score))]
                )],
                       "precision": trained_models[
                           str(models[avg_f1_score.index(max(avg_precision))]
                               )],
                       "roc_auc": trained_models[
                           str(models[avg_f1_score.index(max(avg_roc))]
                                                     )],
                       "accuracy": trained_models[
                           str(models[avg_f1_score.index(max(avg_acc_scores))]
                                                      )],
                       "overall": [trained_models[str(models[i])] for i in overall_best]}

        return best_models

    else:
        avg_neg_mse = []
        avg_neg_mae = []
        avg_r2 = []
        trained_models = {}

        models = model_zoo(task = task)
        scoring_methods = ["neg_mean_squared_error", "neg_mean_absolute_error", "r2"]
        for k in models:  # Training each classification model in model zoo.
            model = k()
            cv = cross_validate(estimator = model, X = X_train, y = y_train, cv = 10, scoring = scoring_methods)
            neg_mse = cv["test_neg_mean_squared_error"]
            neg_mae = cv["test_neg_mean_absolute_error"]
            r2 = cv["test_r2"]
            trained_models[str(k)] = model.fit(X_train, y_train)
            logger.log_params(model.get_params())

            for step in range(len(neg_mse)):
                logger.log_metric(step = step, value = -1 * neg_mse[step], key = "MSE")
                logger.log_metric(step = step, value = -1 * neg_mae[step], key = "MAE")
                logger.log_metric(step = step, value = r2[step], key = "R2")

            avg_neg_mse.append(neg_mse.mean())
            avg_neg_mae.append(neg_mae.mean())
            avg_r2.append(r2.mean())

        performers = [
            avg_neg_mae.index(max(avg_neg_mae)),
            avg_neg_mse.index(max(avg_neg_mse)),
            avg_r2.index(max(avg_r2)),
        ]

        overall_best = multimode(performers)

        best_models = {"MAE": trained_models[
            str(models[avg_neg_mae.index(max(avg_neg_mae))]
                )],
                       "MSE": trained_models[
                           str(models[avg_neg_mse.index(max(avg_neg_mse))]
                                                 )],
                       "R2": trained_models[
                           str(models[avg_r2.index(max(avg_r2))]
                                                )],
                       "overall": [trained_models[str(models[i])] for i in overall_best]}

        return best_models




def training_pipeline(df, target: str, project_name: str):
    """
    The complete training pipeline.
    :param df: The pandas dataframe of the dataset.
    :param target: The name of the target columns.
    :param project_name: The name of the project you are working on.
    :return: Scaled and Training ready features.
    """
    logger = SwiftPredict(project_name = "Testing the Automl")
    new_df = df.drop([target], axis = 1)
    columns = get_dtype_columns(new_df)
    cat_columns = columns["categorical"]
    num_columns = columns["numeric"]

    # Getting the task type
    task = detect_task(df, y = target)

    # Handling null values
    new_df = handle_null_values(new_df)

    # Handling bool dtypes  and Yes No :
    new_df.replace(["True", "False"], [1, 0], inplace=True)
    new_df.replace(["Yes", "No"], [1, 0], inplace=True)

    # Handling categorical data
    for k in new_df.columns.tolist():
        if k in cat_columns:
            num_unique_classes = new_df[k].nunique()
            if num_unique_classes <= 5:  # If the classes in a feature is <= 5, We can use OHE as it won't create dimensionality issues.
                new_df = pd.concat([new_df.drop([k], axis = 1), pd.get_dummies(new_df[k],drop_first = True)], axis = 1)

            else:
                freq_map = df[k].value_counts().to_dict()
                df[f"{k}_frequency"] = df[k].map(freq_map)   # Will map the items to their respective frequencies in the data.

    # Removing unnecessary columns
    corr = new_df.corr()
    direct_corr = [col for col in corr.columns if corr[col].abs().max() == 1]   # Getting the columns having correlation 1
    useful_col_len = len(direct_corr)//2
    while len(direct_corr) > useful_col_len:
        new_df.drop([direct_corr.pop()], inplace = True)

    # Splitting the data
    X = new_df.drop([target], axis = 1)
    y = new_df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify = y, random_state = 21)

    # Scaling numerical data
    std_scaler = StandardScaler()
    X_scaled= std_scaler.fit_transform(X_train)

    # Handling categorical labels
    lbl_encoder = LabelEncoder()
    y_train = lbl_encoder.fit_transform(y_train)

    if task == "classification":
        X_train, y_train = handle_imbalance(new_df, target_column = target, X_train = X_scaled, y_train = y_train )

    best_models = train_model(task = task, X_train = X_train, y_train = y_train, logger = logger)

    return best_models



