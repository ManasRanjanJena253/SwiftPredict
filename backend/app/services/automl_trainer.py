# Importing dependencies
import pandas as pd
from preprocessing import training_pipeline
import pickle

class AutoML:
    def __init__(self, project_name: str, file_path: str):
        self.project_name = project_name
        self.file_path = file_path
        self.data = pd.read_csv(self.file_path)
        self.best_models = {}
        self.std_scaler = None
        self.removed_columns = []
        self.ohe_lst = []
        self.vectorizer_lst = []

    def fit(self, target_column: str):
        self.best_models, self.std_scaler, self.removed_columns, self.ohe_lst, self.vectorizer_lst = training_pipeline(self.data, target_column = target_column,
                                                                                                           project_name = self.project_name)
        return self.best_models

    def export_model(self, model_path: str, key: str = None):
        if not key:
            with open(model_path, 'wb') as f:
                pickle.dump(self.best_models["overall"], f)
        else:
            with open(model_path, 'wb') as f:
                pickle.dump(self.best_models[key], f)

    def predict(self, model, features: list):
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



