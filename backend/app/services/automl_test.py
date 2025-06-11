# Importing dependencies
import pickle
from automl_trainer import AutoML

model_trainer = AutoML()

models = model_trainer.fit(target_column = "Survived", project_name = "Testing the automl", file_path = "tested.csv")

print(models)
model_trainer.export_model(model_path ="../models/models.pkl")
with open('../models/models.pkl', 'rb') as file:
    model = pickle.load(file)

print(model_trainer.evaluate_performance(model))
# data = [[892, 3, "Kelly, Mr. James", "male", 34.5, 0, 0, 330911, 7.8292, "B45", "S"]]
# print(len(data))   # For debugging
# model_trainer.predict(model = model, features = data)