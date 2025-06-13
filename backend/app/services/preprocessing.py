# Importing dependencies
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.metrics import make_scorer, accuracy_score, f1_score, precision_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from app.client.swift_predict import SwiftPredict
from statistics import multimode
import pandas as pd
import numpy as np
from scipy.stats import normaltest
from tqdm.auto import tqdm
import warnings
import string
import spacy
import re
warnings.filterwarnings("ignore")


tqdm.pandas(desc = "Preprocessing text")
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])  # Only keep tagger + lemmatizer for speed

def get_dtype_columns(df):
    """
    Segregates columns in the DataFrame based on their data types.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        dict: Dictionary with keys 'categorical', 'numeric', 'date', and 'bool',
              each mapping to a list of column names of that type.
    """
    cat_columns = df.select_dtypes(include = ["object"]).columns.tolist()
    num_columns = df.select_dtypes(include = ["number"]).columns.tolist()
    date_columns = df.select_dtypes(include = ["datetime64[ns]"]).columns.tolist()
    bool_columns = df.select_dtypes(include = ["bool"]).columns.tolist()

    return {"categorical": cat_columns, "numeric": num_columns, "date": date_columns, "bool": bool_columns}

def text_preprocessor(text: str, handle_emojis: bool = False, handle_html: bool = False) -> str:
    """
    Preprocesses input text:
    - Optionally removes HTML
    - Removes punctuation
    - Removes stopwords
    - Lemmatizes words
    """

    # Optional: Remove HTML
    if handle_html:
        text = re.sub(r'<.*?>', '', text)

    # Removing punctuation
    text = str(text).translate(str.maketrans('', '', string.punctuation))

    # Processing with spaCy
    doc = nlp(text)

    # Lemmatizing and remove stopwords and non-alphabetic tokens
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop]

    if tokens:
        return " ".join(tokens)

def handle_null_values(df):
    """
     Handles missing values in the DataFrame using intelligent strategies.

     Args:
         df (pd.DataFrame): The input DataFrame with potential null values.

     Returns:
         pd.DataFrame: The cleaned DataFrame with nulls handled via dropping,
                       filling with mean/mode, or interpolation.
     """
    total_null_rows = df.isnull().any(axis = 1).sum()   # Will give the total no. of rows having null values.
    total_rows = len(df)  # Gives the total no. of rows in the data.

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
                if k in cat_columns or k in bool_columns:
                    df[k] = df[k].fillna(value = df[k].mode()[0])

                elif k in num_columns:
                    stats, p_value = normaltest(df[k])    # Checking if the data is normally distributed or not.
                    if p_value > 0.05:
                        df[k] = df[k].fillna(value = df[k].mean())
                    else:
                        df[k] = df[k].fillna(value = df[k].mode()[0])

                else :
                    df[k] = df[k].interpolate(method = "time")
        return df

    else:
        return df

def detect_task(df, y: str):
    """
    Detects whether the ML task is classification or regression based on target column.

    Args:
        df (pd.DataFrame): The dataset.
        y (str): The target column name.

    Returns:
        str: 'classification' or 'regression' depending on target data type and distribution.
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
    Applies SMOTE to fix class imbalance in training data if necessary.

    Args:
        df (pd.DataFrame): The original DataFrame.
        target_column (str): Name of the target column.
        X_train (np.ndarray): Training features.
        y_train (np.ndarray or pd.Series): Training labels.

    Returns:
        tuple: Resampled X_train and y_train after applying SMOTE (if needed).
    """
    target = df[target_column]
    class_counts = target.value_counts().tolist()
    max_data = max(class_counts)
    min_data = min(class_counts)

    if min_data/max_data >= 0.15:  # If the min data is less than 15 % of the max data the dataset will be considered imbalanced.
        smote = SMOTE(random_state = 21)
        X_res, target_res = smote.fit_resample(X_train, y_train)

        return X_res, target_res

    else:
        return X_train, y_train

def model_zoo(task, model = None):
    """
    Returns a list of models applicable to the specified ML task.

    Args:
        task (str): The type of ML task ('classification' or 'regression').
        model (object, optional): A specific model to include in the list.

    Returns:
        list: List of model classes corresponding to the task.
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
    Trains multiple models and logs metrics using cross-validation.

    Args:
        task (str): The ML task ('classification' or 'regression').
        X_train (np.ndarray): Training features.
        y_train (np.ndarray or pd.Series): Training labels.
        logger (SwiftPredict): Logger object for metric and parameter logging.
        log_only_best (bool): If set to true only logs the best model.

    Returns:
        tuple:
            - dict: Best models based on individual metrics and overall ranking.
            - dict: Model names for each best-performing metric.
    """
    if task == "classification":
        avg_acc_scores = []
        avg_f1_score = []
        avg_precision = []
        avg_roc = []
        models = model_zoo(task = task)
        trained_models = {}
        scoring_methods = {
            "accuracy": make_scorer(accuracy_score),
            "f1": make_scorer(f1_score, average = 'weighted', zero_division = 0),
            "precision": make_scorer(precision_score, average = 'weighted', zero_division = 0),
            "roc_auc": make_scorer(roc_auc_score, multi_class = 'ovr', average = "weighted")
        }
        for k in tqdm(models, desc = "Training the Models"):     # Training each classification model in model zoo.
            if k.__name__ != "GaussianNB":
                if k.__name__ == "LGBMClassifier":
                    model = k(verbose = -1, n_jobs = -1)
                elif k.__name__ == "LogisticRegression":
                    model = k(solver = "saga", n_jobs = -1)
                else:
                    model = k(n_jobs=-1)
            else :
                model = k()

            cv = cross_validate(estimator = model, X = X_train, y = y_train, cv = 5, scoring = scoring_methods)
            acc = cv["test_accuracy"]
            f1 = cv["test_f1"]
            roc = cv["test_roc_auc"]
            print(roc)
            precision = cv["test_precision"]
            trained_models[str(k)] = model.fit(X_train, y_train)

            for key, value in model.get_params().items():
                logger.log_param(key = key, value = value, model_name = type(model).__name__)

            logger.log_or_update_metric(value = acc.mean(), key = "accuracy", model_name = type(model).__name__)
            logger.log_or_update_metric(value = f1.mean(), key = "f1_score", model_name = type(model).__name__)
            logger.log_or_update_metric(value = roc.mean().item(), key = "roc_auc", model_name = type(model).__name__)
            logger.log_or_update_metric(value = precision.mean(), key = "precision", model_name = type(model).__name__)

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
                           str(models[avg_precision.index(max(avg_precision))]
                               )],
                       "roc_auc": trained_models[
                           str(models[avg_roc.index(max(avg_roc))]
                                                     )],
                       "accuracy": trained_models[
                           str(models[avg_acc_scores.index(max(avg_acc_scores))]
                                                      )],
                       "overall": [trained_models[str(models[i])] for i in overall_best]}

        best_model_showcase = {}

        for metric, model in best_models.items():
            best_model_showcase[metric] = type(model).__name__ if type(model).__name__ != 'list' else [type(k).__name__ for k in model ]

        return best_models, best_model_showcase

    else:
        avg_neg_mse = []
        avg_neg_mae = []
        avg_r2 = []
        trained_models = {}

        models = model_zoo(task = task)
        scoring_methods = ["neg_mean_squared_error", "neg_mean_absolute_error", "r2"]
        for k in tqdm(models, desc = "Training the Models"):  # Training each classification model in model zoo.
            model = k()
            cv = cross_validate(estimator = model, X = X_train, y = y_train, cv = 5, scoring = scoring_methods)
            neg_mse = cv["test_neg_mean_squared_error"]
            neg_mae = cv["test_neg_mean_absolute_error"]
            r2 = cv["test_r2"]
            trained_models[str(k)] = model.fit(X_train, y_train)

            for key, value in model.get_params().items():
                logger.log_param(key = key, value = value, model_name = type(model).__name__)

            logger.log_or_update_metric(value = -1 * neg_mse.mean(), key = "MSE", model_name = type(model).__name__)
            logger.log_or_update_metric(value = -1 * neg_mae.mean(), key = "MAE", model_name = type(model).__name__)
            logger.log_or_update_metric(value = r2.mean(), key = "R2", model_name = type(model).__name__)

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

        best_model_showcase = {}
        for metric, model in best_models.items():
            best_model_showcase[metric] = str(type(model).__name__) if str(type(model).__name__) != 'list' else [str(type(k).__name__) for k in model ]

        return best_models, best_model_showcase

def handle_cat_columns(df, cat_columns, handle_html: bool = False):
    """
    Encodes categorical columns using OneHotEncoding or TF-IDF based on cardinality.

    Args:
        df (pd.DataFrame): The input DataFrame.
        cat_columns (list): List of categorical column names.
        handle_html (bool): If there are html tags in the data or not.

    Returns:
        tuple:
            - pd.DataFrame: Updated DataFrame with encoded categorical columns.
            - list: List of tuples (column index, fitted OneHotEncoder).
            - list: List of tuples (column index, fitted TfidfVectorizer).
    """
    ohe = OneHotEncoder(sparse_output = False, handle_unknown = "ignore")
    ohe_lst = []
    new_df = df
    vectorizer_lst = []
    for k in new_df.columns.tolist():
        if k in cat_columns:
            num_unique_classes = new_df[k].nunique()
            if num_unique_classes <= 5:  # If the classes in a feature is <= 5, We can use OHE as it won't create dimensionality issue

                transformed_array = ohe.fit_transform(new_df[[k]])
                transformed_feature_names = ohe.get_feature_names_out([k])
                transformed_df = pd.DataFrame(transformed_array, columns = transformed_feature_names)

                ohe_lst.append((new_df.columns.get_loc(k), ohe))

                new_df.drop([k], axis = 1, inplace = True)
                new_df = pd.concat([new_df, transformed_df], axis = 1)

            else:
                vectorizer = TfidfVectorizer()
                print(f"Preprocessing column: {k}")
                new_df[k] = new_df[k].progress_apply(lambda x: text_preprocessor(x, handle_html=handle_html))

                tfidf_array = vectorizer.fit_transform(new_df[k].astype(str))

                # Check if there are at least 2 features to apply SVD
                if tfidf_array.shape[1] >= 2:
                    max_components = min(300, tfidf_array.shape[1] - 1)  # n_components must be < n_features
                    svd_temp = TruncatedSVD(n_components=max_components)
                    svd_temp.fit(tfidf_array)

                    cumulative_variance = np.cumsum(svd_temp.explained_variance_ratio_)
                    optimal_components = np.searchsorted(cumulative_variance, 0.95) + 1
                    optimal_components = min(optimal_components, max_components)  # Ensure it doesn't exceed limit

                    svd = TruncatedSVD(n_components=optimal_components)
                    tfidf_reduced = svd.fit_transform(tfidf_array)

                    svd_df = pd.DataFrame(
                        tfidf_reduced,
                        columns=[f"{k}_svd_{i}" for i in range(tfidf_reduced.shape[1])],
                        index=new_df.index
                    )
                    new_df = pd.concat([new_df, svd_df], axis=1)

                    vectorizer_lst.append((new_df.columns.get_loc(k), vectorizer, svd))
                else:
                    print(
                        f"Skipping column '{k}' — Cannot apply SVD.")
                    vectorizer_lst.append((new_df.columns.get_loc(k), vectorizer, None))

                # Drop original column
                new_df.drop(columns=[k], inplace=True)
    return new_df, ohe_lst, vectorizer_lst

def training_pipeline(df, target_column: str, project_name: str, drop_name: bool = True, drop_id: bool = True):
    """
       Executes a complete training pipeline: preprocessing, feature engineering,
       imbalance handling, model training, and logging.

       Args:
           df (pd.DataFrame): Input dataset.
           target_column (str): Name of the target column.
           project_name (str): Name of the project for logging.
           drop_id (bool): If set to true removes the columns with name == ID or id or index.
           drop_name (bool): If set to true removes the columns with name == name or Name.

       Returns:
           tuple:
               - dict: Trained models categorized by metric and overall performance.
               - StandardScaler: Scaler used on numeric features.
               - list: Indices of removed highly correlated features.
               - list: One-hot encoders used with their column indices.
               - list: TF-IDF vectorizers used with their column indices.
               - np.ndarray: Scaled test features.
               - pd.Series: Test labels.
               - dict: Best model names for each metric.
       """
    logger = SwiftPredict(project_name = project_name, project_type = "ML")
    new_df = df
    target = df[target_column]
    # Handling categorical labels

    if target.dtype == "object":
        lbl_encoder = LabelEncoder()
        new_df[target_column] = lbl_encoder.fit_transform(target)

    """if drop_name:
        new_df.drop([col for col in new_df.columns.tolist() if col.lower() == "name"], axis = 1, inplace = True)

    if drop_id:
        new_df.drop([col for col in new_df.columns.tolist() if col.lower() == "id" or "index"], axis = 1, inplace = True)"""

    columns = get_dtype_columns(new_df)
    cat_columns = columns["categorical"]
    #print(cat_columns)  # For debugging
    num_columns = columns["numeric"]
    #print(num_columns)  # For debugging
    ohe_lst = []
    vectorizer_lst = []

    # Getting the task type
    task = detect_task(new_df, y = target_column)

    # Handling null values
    new_df = handle_null_values(new_df)

    # Handling bool dtypes  and Yes No :
    new_df.replace(["True", "False"], [1, 0], inplace = True)
    new_df.replace(["Yes", "No"], [1, 0], inplace = True)

    # Handling categorical data
    if cat_columns:
        new_df, ohe_lst, vectorizer_lst = handle_cat_columns(df = new_df, cat_columns = cat_columns)

    # Removing unnecessary columns
    corr = new_df[[col for col in num_columns if col != target_column]].corr()
    direct_corr = [col for col in corr.columns if
                   corr[col].abs().max() == 1]  # Getting the columns having correlation 1
    useful_col_len = len(direct_corr) // 2
    removed_columns = []
    while len(direct_corr) > useful_col_len:
        removed_columns.append(new_df.columns.get_loc(direct_corr[- 1]))  # Appending the index of the removed columns
        new_df.drop([direct_corr.pop()], inplace = True, axis = 1)

    new_df = handle_null_values(new_df)   # Ensuring before splitting that no null values are created due to preprocessing.

    # Splitting the data
    X = new_df.drop([target_column], axis = 1)
    y = new_df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify = y, random_state = 21)

    # Scaling numerical data
    std_scaler = StandardScaler()
    X_scaled = std_scaler.fit_transform(X_train)
    X_test = std_scaler.transform(X_test)

    if task == "classification":
        X_train, y_train = handle_imbalance(df, target_column = target_column, X_train = X_scaled, y_train = y_train)

    best_models, best_model_showcase = train_model(task = task, X_train = X_train, y_train = y_train, logger = logger)

    return best_models, std_scaler, removed_columns, ohe_lst, vectorizer_lst, X_test, y_test, best_model_showcase, new_df