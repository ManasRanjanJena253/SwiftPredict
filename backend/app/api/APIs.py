# Importing dependencies
from fastapi import FastAPI
import uuid
from datetime import datetime
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
from io import BytesIO
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["SwiftPredict"]
run = db["Run"]

@app.post("/{project_name}/runs/{run_id}/log_param")
async def log_param(key: str, value, run_id: str, project_name: str):
    """
    Used to log the parameters used when training a certain model.
    :param key: The name of the parameter.
    :param value: The value given/assigned to that parameter.
    :param run_id: The unique run_id of that particular model.
    :param project_name: The name of the project.
    :return: The updated data.
    """
    data = await run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        param = {"run_id": run_id, "key": key, "value": value, "created_at": datetime.now(), "project_name": project_name}
        await run.insert_one(param)
        return await run.find_one({"run_id": run_id}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/log_metric")
async def log_metric(key: str, value, step: int, run_id: str, project_name: str):
    """
    Used to log the metrics used for evaluation of the model.
    :param key: The name of the metric
    :param value: The value of the metric calculated.
    :param run_id: The unique run_id of that particular parameter.
    :param step: The iteration at which the value of the metrics is being given.
    :param project_name: The name of the project.
    :return: The updated data.
    """
    data = await run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        await run.update_one({"run_id": run_id, "project_name": project_name},
                             {"$set": {"metrics.metric": key},
                              "$push": {"metrics.details.step": float(step), "metrics.details.values": float(value)}})

        return await run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})

    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/add_tags")
async def add_tags(run_id: str, project_name: str, tags: list):
    """
    Used to add tags to already created runs.
    :param run_id: The unique run_id associated with a run.
    :param project_name: The name of the project.
    :param tags: List of tags you want to provide to a particular run.
    :return: The updated data.
    """
    data = await run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        await run.update_one({"run_id": run_id, "project_name": project_name},
                             {"$push": {"tags": tags}})
        return run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/update_status")
async def update_status(run_id: str, project_name: str, status: str):
    """
    Used to add tags to already created runs.
    :param run_id: The unique run_id associated with a run.
    :param project_name: The name of the project.
    :param status: The current running status of the project.
    :return: The updated data.
    """
    data = await run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        await run.update_one({"run_id": run_id, "project_name": project_name},
                             {"status": status})
        return run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/add_notes")
async def add_notes(run_id: str, project_name: str, notes: str):
    """
    Used to add tags to already created runs.
    :param run_id: The unique run_id associated with a run.
    :param project_name: The name of the project.
    :param notes: For experiment description/logging.
    :return: The updated data.
    """
    data = await run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        await run.update_one({"run_id": run_id, "project_name": project_name},
                             {"notes": notes})
        return run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}


@app.get("/{project_name}/runs/{run_id}")
async def fetch_run_id(run_id: str, project_name: str):
    """
    Used to fetch all the data associated with a specific run_id .
    :param run_id: The unique run_id of a particular code run.
    :param project_name: The name of the project.
    :return: The updated data.
    """
    docs = await run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    if docs:
        return docs
    else:
        return {"Error": f"Run_Id : {run_id}, DOESN'T EXIST"}

@app.get("/projects")
async def get_all_projects():
    """
    Used to get all distinct projects you have created.
    :return: List of projects.
    """
    projects = await run.distinct("project_name")
    if projects:
        return projects
    else:
        return {"Error": "No, Projects made/saved yet."}

@app.get("/{project_name}/plots")
async def plot_metrics(metric: str, run_id: str, project_name: str):
    """
    This function takes in the metric name and a list containing dicts containing each iteration(step) and metric value at that instance.
    :param metric: Name of the metric.
    :param run_id: The unique run_id of a particular code run.
    :param project_name: The name of the project.
    :return: Streaming Image.
    """
    data = await run.find_one({"run_id": run_id, "project_name": project_name, "metrics.metric": metric.lower()})
    if data:
        values = data["metrics"]["details"]
        steps = values["step"]
        iter_values = values["value"]

        plt.figure()
        plt.plot(steps, iter_values)
        plt.xlabel("Step")
        plt.ylabel(metric.title())
        plt.title(f"{metric.title()} Over Time")

        # fig = plt.gcf()
        # return fig, This statement will raise an error as fig is a python object and not a web serializable response, So we need to stream this in the form of binary streams.

        buf = BytesIO()
        plt.savefig(buf, format = "png")
        buf.seek(0)

        return StreamingResponse(buf, media_type = "image/png")

    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST OR The metrics field DOESN'T EXIST."}

if __name__ == '__main__':   # Code to run the code without using the command prompt.
    uvicorn.run(app, host = '127.0.0.1', port = 9000)