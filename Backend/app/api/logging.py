# Importing dependencies
from Backend.app.core.config import db
from fastapi import FastAPI
import uuid
from datetime import datetime
run = db["Run"]
app = FastAPI()

@app.post("/log_param")
async def log_param(key: str, value, created_at, run_id: str, project_name: str):
    """
    Used to log the parameters used when training a certain model.
    :param key: The name of the parameter.
    :param value: The value given/assigned to that parameter.
    :param run_id: The unique run_id of that particular model.
    :param created_at: The time at which the data was logged in.
    :param project_name: The name of the project.
    :return: JSON
    """
    param = {"run_id": run_id, "key": key, "value": value, "created_at": created_at, "project_name": project_name}
    await run.insert_one(param)

    return run.find_one({"run_id": run_id})

@app.post("/log_metric")
async def log_metric(key: str, value, step: int, run_id: str, project_name: str):
    """
    Used to log the metrics used for evaluation of the model.
    :param key: The name of the metric
    :param value: The value of the metric calculated.
    :param run_id: The unique run_id of that particular parameter.
    :param step: The iteration at which the value of the metrics is being given.
    :param project_name: The name of the project.
    :return: JSON
    """
    metric = {"step": step, "value": value}
    await run.update_one({"run_id": run_id, "key": key, "project_name": project_name}, {"$push": {"items": metric}})  # Appending the steps into the array of metrics, to create a time series data to plot more easily.
    return run.find_one({"run_id": run_id, "key": key, "project_name": project_name})


