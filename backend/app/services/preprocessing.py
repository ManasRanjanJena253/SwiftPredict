# Importing dependencies
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np

def get_dtype_columns(df):
    """
    Gives all the columns segregated on the basis of their dtypes.
    :param df: The pandas dataframe of the dataset.
    :return: A dictionary containing the dtype as key and the list of columns of that dtype as values.
    """
    cat_columns = df.select_dtypes(include = ["object"]).columns.tolist()
    num_columns = df.select_dtypes(exclude = ["object"]).columns.tolist()
    date_columns = df.select_dtypes(include = ["datetime64[ns]"]).columns.tolist()

    return {"categorical": cat_columns, "numeric": num_columns, "date": date_columns}

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
            null_columns = df.isnull().columns.tolist()
            cat_columns = columns["categorical"]
            num_columns = columns["numeric"]
            date_columns = columns["date"]

