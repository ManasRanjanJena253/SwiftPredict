import pandas as pd
from preprocessing import training_pipeline, detect_task
from sklearn.metrics import accuracy_score, f1_score, precision_score, roc_auc_score, mean_squared_error, mean_absolute_error, r2_score
import pickle
from typing import Any
from preprocessing import text_preprocessor
class AutoML:
    """
    AutoML is a lightweight wrapper class designed to automate data preprocessing,
    model training, evaluation, and export for both classification and regression tasks.

    Attributes:
        project_name (str): Name of the current project or experiment.
        file_path (str): Path to the dataset CSV file.
        data (pd.DataFrame): Loaded dataset used for training.
        best_models (dict): Dictionary containing best models for various metrics and an 'overall' best.
        std_scaler (StandardScaler): Scaler object for standardizing numerical features.
        removed_columns (list): List of columns removed during preprocessing.
        ohe_lst (list): List of tuples (column, encoder) for one-hot encoded categorical columns.
        vectorizer_lst (list): List of tuples (column, vectorizer, svd) for text features.
        X_test (pd.DataFrame): Test features reserved for evaluation.
        y_test (pd.Series): Test target labels corresponding to X_test.
        target_column (str): Name of the target column in the dataset.
        task (str): Type of ML task, either 'classification' or 'regression'.
        modified_df : The updated pandas df.
    """

    def __init__(self):
        self.project_name = ''
        self.file_path = ''
        self.data = None
        self.best_models = {}
        self.std_scaler = None
        self.removed_columns = []
        self.ohe_lst = []
        self.vectorizer_lst = []
        self.X_test = Any
        self.y_test = Any
        self.target_column = ''
        self.task = None
        self.modified_df = Any

    def fit(self, project_name: str, file_path: str, target_column: str, drop_id: bool = True, drop_name: bool = True) -> dict:
        """
        Trains models on the provided dataset using the AutoML pipeline.

        Args:
            project_name (str): Name of the project to associate with this run.
            file_path (str): Path to the input CSV file.
            target_column (str): Column name to be predicted (label column).
            drop_name (bool): Columns name with name or Name will be dropped.
            drop_id (bool): Columns with column name == id or ID will be removed.

        Returns:
            dict: Dictionary containing the best model names (string) for each metric and the overall best model.
        """
        self.project_name = project_name
        self.file_path = file_path
        self.target_column = target_column
        self.data = pd.read_csv(self.file_path)
        self.task = detect_task(df=self.data, y=self.target_column)

        self.best_models, self.std_scaler, self.removed_columns, self.ohe_lst, self.vectorizer_lst, self.X_test, self.y_test, best_model_showcase, self.modified_df = (training_pipeline(
            self.data, target_column = self.target_column, project_name = self.project_name, drop_name = drop_name, drop_id = drop_id
        ))
        return best_model_showcase

    def export_model(self, model_path: str, key: str = None) -> None:
        """
        Exports the best trained model to a file using pickle.

        Args:
            model_path (str): The file path to save the serialized model.
            key (str, optional): The metric key for selecting a specific best model.
                                 If None, the overall best model is saved.

        Returns:
            None
        """
        model_to_export = self.best_models["overall"][0] if not key else self.best_models[key]
        with open(model_path, 'wb') as f:
            pickle.dump(model_to_export, f)

    def _preprocessing(self, features: dict) -> Any:
        """
        Preprocesses raw input features before prediction, based on the pipeline fitted during training.

        Args:
            features (dict): Dictionary containing raw input features.

        Returns:
            np.ndarray: Preprocessed and scaled feature array ready for prediction.
        """
        if self.ohe_lst:
            for k, ohe in self.ohe_lst:
                features[k] = ohe.transform([features[k]])

        if self.vectorizer_lst :
            for k, vectorizer, svd in self.vectorizer_lst:
                features[k] = vectorizer.transform([features[k]])
                features[k] = svd.transform([features[k]])

        if self.removed_columns:
            for k in self.removed_columns:
                features.pop(k, None)

        processed_features = self.std_scaler.transform([features])
        return processed_features

    def evaluate_performance(self, model = None, key: str = None) -> dict:
        """
        Evaluates model performance using stored test data.

        Args:
            model (Any, optional): A trained model instance to evaluate.
            key (str, optional): If model is None, key to select from best_models.

        Returns:
            dict: A dictionary of evaluation metrics.

        Raises:
            ValueError: If neither model nor key is provided.
        """
        def eval_params(model_instance):
            y_pred = model_instance.predict(self.X_test)
            if self.task == "classification":
                return {
                    "accuracy": accuracy_score(self.y_test, y_pred),
                    "f1": f1_score(self.y_test, y_pred, average = "weighted"),
                    "roc_auc": roc_auc_score(self.y_test, y_pred, average = "weighted", multi_class = "ovr").item(),
                    "precision": precision_score(self.y_test, y_pred, average = "weighted")
                }
            else:
                return {
                    "MSE": mean_squared_error(self.y_test, y_pred),
                    "MAE": mean_absolute_error(self.y_test, y_pred),
                    "R2": r2_score(self.y_test, y_pred).item()
                }

        if model:
            return eval_params(model_instance = model)
        elif key:
            return eval_params(model_instance = self.best_models[key])
        else:
            raise ValueError("Either a model or key must be provided.")

    def predict(self, model, features: dict) -> Any:
        """
        Predicts target values using the trained model on new data.

        Args:
            model (Any): Trained model instance (e.g., XGBClassifier).
            features (dict): Raw feature inputs as a dictionary.

        Returns:
            np.ndarray: Model predictions.
        """
        processed_features = self._preprocessing(features = features)
        return model.predict(processed_features)
