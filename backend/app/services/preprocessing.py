# Importing dependencies
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
# ADDED CATBOOST IMPORTS HERE
from catboost import CatBoostClassifier, CatBoostRegressor 
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.metrics import make_scorer, accuracy_score, f1_score, precision_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from ..client.swift_predict import SwiftPredict
from statistics import multimode
import pandas as pd
import numpy as np
from scipy.stats import normaltest
from tqdm.auto import tqdm
import warnings
import string
import re
warnings.filterwarnings("ignore")

tqdm.pandas(desc = "Preprocessing text")

import spacy
from spacy.cli import download

try:
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
except OSError:
    print("SwiftPredict: Downloading required spaCy language model (en_core_web_sm)...")
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

def get_dtype_columns(df):
    cat_columns = df.select_dtypes(include = ["object"]).columns.tolist()
    num_columns = df.select_dtypes(include = ["number"]).columns.tolist()
    date_columns = df.select_dtypes(include = ["datetime64[ns]"]).columns.tolist()
    bool_columns = df.select_dtypes(include = ["bool"]).columns.tolist()
    return {"categorical": cat_columns, "numeric": num_columns, "date": date_columns, "bool": bool_columns}

def text_preprocessor(text: str, handle_emojis: bool = False, handle_html: bool = False) -> str:
    if handle_html:
        text = re.sub(r'<.*?>', '', text)
    text = str(text).translate(str.maketrans('', '', string.punctuation))
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop]
    return " ".join(tokens) if tokens else ""

def handle_null_values(df):
    total_null_rows = df.isnull().any(axis = 1).sum()
    total_rows = len(df)
    if total_null_rows:
        if total_null_rows <= (0.1 * total_rows):
            df.dropna(inplace = True)
            return df
        else:
            columns = get_dtype_columns(df = df)
            null_columns = df.columns[df.isnull().any(axis=0)].tolist()
            cat_columns = columns["categorical"]
            bool_columns = columns["bool"]
            num_columns = columns["numeric"]
            for k in null_columns:
                if k in cat_columns or k in bool_columns:
                    df[k] = df[k].fillna(value = df[k].mode()[0])
                elif k in num_columns:
                    stats, p_value = normaltest(df[k])
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
    target = df[y]
    if target.dtype == "object" or target.dtype.name == "category":
        return "classification"
    elif np.issubdtype(target.dtype, np.integer):
        return "classification" if target.nunique() <= 20 else "regression"
    elif np.issubdtype(target.dtype, np.floating):
        return "regression"

def handle_imbalance(df, target_column : str, X_train, y_train):
    target = df[target_column]
    class_counts = target.value_counts().tolist()
    if min(class_counts)/max(class_counts) < 0.15:
        smote = SMOTE(random_state = 21)
        X_res, target_res = smote.fit_resample(X_train, y_train)
        return X_res, target_res
    return X_train, y_train

def model_zoo(task, model = None):
    # UPDATED MODEL ZOO WITH CATBOOST
    if task == "classification":
        models = [GaussianNB, XGBClassifier, RandomForestClassifier, LGBMClassifier, LogisticRegression, CatBoostClassifier]
    else:
        models = [LinearRegression, XGBRegressor, LGBMRegressor, RandomForestRegressor, CatBoostRegressor]
    
    if model:
        models.append(model)
    return models

def train_model(task, X_train, y_train, logger = None):
    if task == "classification":
        avg_acc_scores, avg_f1_score, avg_precision = [], [], []
        models = model_zoo(task = task)
        trained_models = {}
        scoring_methods = {
            "accuracy": make_scorer(accuracy_score),
            "f1": make_scorer(f1_score, average = 'weighted', zero_division = 0),
            "precision": make_scorer(precision_score, average = 'weighted', zero_division = 0)
        }
        for k in tqdm(models, desc = "Training the Models"):
            if k.__name__ == "LGBMClassifier":
                model = k(verbose = -1, n_jobs = -1)
            elif k.__name__ == "LogisticRegression":
                model = k(solver = "saga", n_jobs = -1)
            # ADDED CATBOOST CONSTRUCTOR LOGIC
            elif k.__name__ == "CatBoostClassifier":
                model = k(verbose=0, allow_writing_files=False)
            elif k.__name__ == "GaussianNB":
                model = k()
            else:
                model = k(n_jobs=-1)

            cv = cross_validate(estimator = model, X = X_train, y = y_train, cv = 5, scoring = scoring_methods)
            acc, f1, precision = cv["test_accuracy"], cv["test_f1"], cv["test_precision"]
            trained_models[str(k)] = model.fit(X_train, y_train)

            for key, value in model.get_params().items():
                logger.log_param(key = key, value = value, model_name = type(model).__name__)

            logger.log_or_update_metric(value = acc.mean(), key = "accuracy", model_name = type(model).__name__)
            logger.log_or_update_metric(value = f1.mean(), key = "f1_score", model_name = type(model).__name__)
            logger.log_or_update_metric(value = precision.mean(), key = "precision", model_name = type(model).__name__)

            avg_precision.append(precision.mean()); avg_f1_score.append(f1.mean()); avg_acc_scores.append(acc.mean())

        performers = [avg_acc_scores.index(max(avg_acc_scores)), avg_f1_score.index(max(avg_f1_score)), avg_precision.index(max(avg_precision))]
        overall_best = multimode(performers)
        best_models = {
            "f1": trained_models[str(models[avg_f1_score.index(max(avg_f1_score))])],
            "precision": trained_models[str(models[avg_precision.index(max(avg_precision))])],
            "accuracy": trained_models[str(models[avg_acc_scores.index(max(avg_acc_scores))])],
            "overall": [trained_models[str(models[i])] for i in overall_best]
        }
        best_model_showcase = {metric: (type(model).__name__ if not isinstance(model, list) else [type(k).__name__ for k in model]) for metric, model in best_models.items()}
        return best_models, best_model_showcase

    else:
        avg_neg_mse, avg_neg_mae, avg_r2 = [], [], []
        trained_models = {}
        models = model_zoo(task = task)
        scoring_methods = ["neg_mean_squared_error", "neg_mean_absolute_error", "r2"]
        for k in tqdm(models, desc = "Training the Models"):
            # ADDED CATBOOST REGRESSOR CONSTRUCTOR LOGIC
            if k.__name__ == "CatBoostRegressor":
                model = k(verbose=0, allow_writing_files=False)
            elif k.__name__ in ["XGBRegressor", "LGBMRegressor", "RandomForestRegressor"]:
                model = k(n_jobs=-1) if k.__name__ != "LGBMRegressor" else k(verbose=-1, n_jobs=-1)
            else:
                model = k()
                
            cv = cross_validate(estimator = model, X = X_train, y = y_train, cv = 5, scoring = scoring_methods)
            neg_mse, neg_mae, r2 = cv["test_neg_mean_squared_error"], cv["test_neg_mean_absolute_error"], cv["test_r2"]
            trained_models[str(k)] = model.fit(X_train, y_train)

            for key, value in model.get_params().items():
                logger.log_param(key = key, value = value, model_name = type(model).__name__)

            logger.log_or_update_metric(value = -1 * neg_mse.mean(), key = "MSE", model_name = type(model).__name__)
            logger.log_or_update_metric(value = -1 * neg_mae.mean(), key = "MAE", model_name = type(model).__name__)
            logger.log_or_update_metric(value = r2.mean(), key = "R2", model_name = type(model).__name__)

            avg_neg_mse.append(neg_mse.mean()); avg_neg_mae.append(neg_mae.mean()); avg_r2.append(r2.mean())

        performers = [avg_neg_mae.index(max(avg_neg_mae)), avg_neg_mse.index(max(avg_neg_mse)), avg_r2.index(max(avg_r2))]
        overall_best = multimode(performers)
        best_models = {
            "MAE": trained_models[str(models[avg_neg_mae.index(max(avg_neg_mae))])],
            "MSE": trained_models[str(models[avg_neg_mse.index(max(avg_neg_mse))])],
            "R2": trained_models[str(models[avg_r2.index(max(avg_r2))])],
            "overall": [trained_models[str(models[i])] for i in overall_best]
        }
        best_model_showcase = {metric: (str(type(model).__name__) if not isinstance(model, list) else [str(type(k).__name__) for k in model]) for metric, model in best_models.items()}
        return best_models, best_model_showcase

def handle_cat_columns(df, cat_columns, handle_html: bool = False):
    ohe = OneHotEncoder(sparse_output = False, handle_unknown = "ignore")
    ohe_lst, vectorizer_lst = [], []
    temp_df, new_df = df.copy(), df.copy()
    for k in new_df.columns.tolist():
        index = temp_df.columns.get_loc(k)
        if k in cat_columns:
            if new_df[k].nunique() <= 5:
                transformed_df = pd.DataFrame(ohe.fit_transform(new_df[[k]]), columns = ohe.get_feature_names_out([k]))
                ohe_lst.append((index, ohe))
                new_df.drop([k], axis = 1, inplace = True)
                new_df = pd.concat([new_df, transformed_df], axis = 1)
            else:
                vectorizer = TfidfVectorizer()
                new_df[k] = new_df[k].progress_apply(lambda x: text_preprocessor(x, handle_html = handle_html))
                tfidf_array = vectorizer.fit_transform(new_df[k].astype(str))
                if tfidf_array.shape[1] >= 2:
                    max_comp = min(300, tfidf_array.shape[1] - 1)
                    svd_temp = TruncatedSVD(n_components = max_comp).fit(tfidf_array)
                    opt_comp = min(np.searchsorted(np.cumsum(svd_temp.explained_variance_ratio_), 0.95) + 1, max_comp)
                    svd = TruncatedSVD(n_components = opt_comp)
                    tfidf_red = svd.fit_transform(tfidf_array)
                    svd_df = pd.DataFrame(tfidf_red, columns = [f"{k}_svd_{i}" for i in range(tfidf_red.shape[1])], index = new_df.index)
                    new_df = pd.concat([new_df, svd_df], axis = 1)
                    vectorizer_lst.append((index, vectorizer, svd))
                else:
                    vectorizer_lst.append((index, vectorizer, None))
                new_df.drop(columns=[k], inplace=True)
    return new_df, ohe_lst, vectorizer_lst

def training_pipeline(df, target_column: str, project_name: str, drop_name: bool = True, drop_id: bool = True):
    logger = SwiftPredict(project_name = project_name, project_type = "ML")
    new_df, target = df.copy(), df[target_column]
    removed_columns = []
    if target.dtype == "object":
        new_df[target_column] = LabelEncoder().fit_transform(target)
    new_df.replace(["True", "False", "Yes", "No"], [1, 0, 1, 0], inplace = True)
    if drop_name:
        cols = [c for c in new_df.columns if c.lower() == "name"]
        for c in cols: removed_columns.append(new_df.columns.get_loc(c))
        new_df.drop(cols, axis = 1, inplace = True)
    if drop_id:
        cols = [c for c in new_df.columns if "id" in c.lower() or "index" in c.lower()]
        for c in cols: removed_columns.append(new_df.columns.get_loc(c))
        new_df.drop(cols, axis = 1, inplace = True)
    
    cols = get_dtype_columns(new_df)
    task = detect_task(new_df, y = target_column)
    new_df = handle_null_values(new_df)
    if cols["categorical"]:
        new_df, ohe_lst, vec_lst = handle_cat_columns(df = new_df, cat_columns = [c for c in cols["categorical"] if c not in removed_columns])
    
    num_cols = cols["numeric"]
    corr = new_df[[c for c in num_cols if c != target_column]].corr()
    direct_corr = [c for c in corr.columns if corr[c].abs().max() == 1]
    while len(direct_corr) > (len(direct_corr) // 2):
        removed_columns.append(new_df.columns.get_loc(direct_corr[-1]))
        new_df.drop([direct_corr.pop()], inplace = True, axis = 1)
    
    new_df = handle_null_values(new_df)
    X, y = new_df.drop([target_column], axis = 1), new_df[target_column]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify = y if task == "classification" else None, random_state = 21)
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X_tr)
    X_te = scaler.transform(X_te)
    if task == "classification":
        X_tr, y_tr = handle_imbalance(new_df, target_column = target_column, X_train = X_sc, y_train = y_tr)
    
    best_m, best_s = train_model(task = task, X_train = X_tr, y_train = y_tr, logger = logger)
    return best_m, scaler, removed_columns, ohe_lst, vec_lst, X_te, y_te, best_s, new_df
