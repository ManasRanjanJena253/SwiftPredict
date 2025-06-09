# Importing dependencies
import pickle
from automl_trainer import AutoML

model_trainer = AutoML(project_name = "Testing the automl", file_path = "tested.csv")

models = model_trainer.fit(target_column = "Survived")

print(models)
model_trainer.export_model(model_path = "models.pkl")
with open('models.pkl', 'rb') as file:
    model = pickle.load(file)

data = [[892, 3, "Kelly, Mr. James", "male", 34.5, 0, 0, 330911, 7.8292, "B45", "S"]]
print(len(data))   # For debugging
model_trainer.predict(model = model, features = data)