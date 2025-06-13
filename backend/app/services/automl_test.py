# Importing dependencies
import pickle
from automl_trainer import AutoML
import pandas as pd

data = pd.read_csv("tested.csv")

model_trainer = AutoML()

models = model_trainer.fit(target_column = "sentiment", project_name = "Sentiment Analysis", file_path = "train.csv")

print(models)
model_trainer.export_model(model_path ="../models/models.pkl")
with open('../models/models.pkl', 'rb') as file:
    model = pickle.load(file)

model_trainer.modified_df.to_csv("Modified_df.csv")
print("Original df : ", model_trainer.data.head())
print("Modified df : ", model_trainer.modified_df)

print(model_trainer.evaluate_performance(model))
# data = [[892, 3, "Kelly, Mr. James", "male", 34.5, 0, 0, 330911, 7.8292, "B45", "S"]]
# print(len(data))   # For debugging
# model_trainer.predict(model = model, features = data)