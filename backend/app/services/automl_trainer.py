# Importing dependencies
import pandas as pd
from preprocessing import training_pipeline, detect_task
from sklearn.metrics import accuracy_score, f1_score, precision_score, roc_auc_score, mean_squared_error, mean_absolute_error, r2_score
import pickle
from typing import Any

class AutoML:
    """
    An AutoML class that can be used to Train, ML models on any dataset without going through the usual model training cycle of preprocessing and comparing hundreds
    of models.
    """
    def __init__(self, project_name: str, file_path, target_column: str):
        self.project_name = project_name
        self.file_path = file_path
        self.data = pd.read_csv(self.file_path)
        self.best_models = {}
        self.std_scaler = None
        self.removed_columns = []
        self.ohe_lst = []
        self.vectorizer_lst = []
        self.X_test = Any
        self.y_test = Any
        self.target_column = target_column
        self.task = detect_task(df = self.data, y = self.target_column)

    def fit(self):
        """
        Used for fitting the model to the data for training the models.
        :return: The best model for each evaluation metric and the overall best model in the form of dict.
        """
        self.best_models, self.std_scaler, self.removed_columns, self.ohe_lst, self.vectorizer_lst, self.X_test, self.y_test = training_pipeline(
            self.data, target_column = self.target_column,project_name = self.project_name
        )
        return self.best_models

    def export_model(self, model_path: str, key: str = None):
        """
        Used to export/download the desired trained model. By default, downloads the overall best model.
        :param model_path: The path of the file where you want to save the model.
        :param key: The parameter name of which best model you want to download.
        :return: None.
        """
        if not key:
            with open(model_path, 'wb') as f:
                pickle.dump(self.best_models["overall"], f)
        else:
            with open(model_path, 'wb') as f:
                pickle.dump(self.best_models[key], f)

    def _preprocessing(self, features):
        """
        The preprocessing pipeline for the raw data, that the model haven't seen before.
        :param features:
        :return:
        """
        if self.ohe_lst:
            for k, ohe in self.ohe_lst:
                features[k] = ohe.transform([features[k]])

        if self.vectorizer_lst:
            for k, vectorizer in self.vectorizer_lst:
                features[k] = vectorizer.transform([features[k]])

        if self.removed_columns:
            for k in self.removed_columns:
                features.pop(k)

        scaled_features = self.std_scaler.transform([features])

        return scaled_features

    def evaluation_performance(self, model = None, key: str = None):
        """
        Used to get the performance of the provided model or key on the test_data which is created while training.
        :param model: The exported model.
        :param key: The metric whose best model you want to test on test data.
        :return: The value of various metrics for
        """
        def eval_params(model):
            metrics_dict = {}
            y_pred = model.predict(self.X_test)
            if self.task == "classification":
                metrics_dict["accuracy"] = accuracy_score(self.y_test, y_pred)
                metrics_dict["f1"] = f1_score(self.y_test, y_pred)
                metrics_dict["roc_auc"] = roc_auc_score(self.y_test, y_pred)
                metrics_dict["precision"] = precision_score(self.y_test, y_pred)
                return metrics_dict

            else:
                metrics_dict["MSE"] = mean_squared_error(self.y_test, y_pred)
                metrics_dict["MAE"] = mean_absolute_error(self.y_test, y_pred)
                metrics_dict["R2"] = r2_score(self.y_test, y_pred)
                return metrics_dict
        if model:
            return eval_params(model = model)

        elif key:
            model = self.best_models[key]
            return eval_params(model = model)

        else:
            return "Error !! Plz provide with either key or model."

    def predict(self, model, features: list):
        """
        Used for get the prediction of model on the data provided.
        :param model: The exported model.
        :param features: A 2D list of the features.
        :return: The predicted label/value.
        """
        print(self.ohe_lst)
        print(len(features))
        if self.ohe_lst:
            for k, ohe in self.ohe_lst:
                features[k] = ohe.transform([features[k]])

        if self.vectorizer_lst:
            for k, vectorizer in self.vectorizer_lst:
                features[k] = vectorizer.transform([features[k]])

        if self.removed_columns:
            for k in self.removed_columns:
                features.pop(k)

        scaled_features = self.std_scaler.transform([features])

        return model.predict(scaled_features)



