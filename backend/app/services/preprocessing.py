# Importing dependencies
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
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

def handle_null_values(file):
    """
    Handles the null values in a dataset.
    :param file: The dataset in the format of csv.
    :return: A df after all null value issues have been resolved.
    """
    df = pd.read_csv(file)
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

def feature_engineering(df, X_train, y_train):
    """
    For doing the complete feature engineering process.
    :param df: The pandas dataframe of the dataset.
    :param X_train: The training features
    :param y_train: The target.
    :return: Scaled and Training ready features.
    """
    X = X_train
    y = y_train
    columns = get_dtype_columns(df)










