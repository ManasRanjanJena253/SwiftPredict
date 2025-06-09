# Importing dependencies
from fastapi import FastAPI
from app.services.automl_trainer import AutoML

app = FastAPI()
model_trainer = AutoML(project_name=project_name, file_path=file)

@app.post("/automl/train")
def train_model(file, project_name: str, target_column: str):
    """
    Used to provide the api with necessary data for training the model.
    :param file: The csv file of the dataset.
    :param project_name: The name of the project the dataset belongs to.
    :param target_column: The name of the target column.
    :return: The best models and parameters after training.
    """
    best_models = model_trainer.fit()
    return best_models

@app.get("/automl/predict")
def predict(data):
    """
    Used to get the prediction made by the model provided or the best_model on the data.
    :param data: The data upon which to make predictions
    :return: predicted value.
    """



