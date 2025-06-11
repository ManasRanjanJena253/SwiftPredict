# Importing dependencies
from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import uvicorn

app = FastAPI()
client = MongoClient(host = "localhost", port = 27017)
origins = ["http://localhost:3000"]  # matching the React dev port

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

db = client["SwiftPredict"]
run = db["Run"]

@app.get("/")
def welcome():
    """
    Root endpoint for API.

    Returns:
        dict: Welcome message for the SwiftPredict platform.
    """
    return {"Welcome": "SwiftPredict: Your compass from data to discovery."}

@app.post("/{project_name}/runs/{run_id}/log_param")
def log_param(key: str, value, run_id: str, project_name: str):
    """
    Logs a single parameter for a specific run of a project.

    Args:
        key (str): Name of the parameter.
        value (Any): Value of the parameter.
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.

    Returns:
        dict: Updated run data or error message.
    """
    data = run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        param = {"run_id": run_id, "key": key, "value": value, "created_at": datetime.now(), "project_name": project_name}
        run.insert_one(param)
        return run.find_one({"run_id": run_id}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/log_metric")
def log_metric(key: str, value, step: int, run_id: str, project_name: str):
    """
    Logs a metric value at a given step for a specific run.

    Args:
        key (str): Metric name (e.g., accuracy, loss).
        value (float): Metric value.
        step (int): Training step or epoch.
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.

    Returns:
        dict: Updated run data or error message.
    """
    data = run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        run.update_one({"run_id": run_id, "project_name": project_name},
                             {"$set": {"metrics.metric": key},
                              "$push": {"metrics.details.step": float(step), "metrics.details.values": float(value)}})

        return run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})

    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/add_tags")
def add_tags(run_id: str, project_name: str, tags: list):
    """
    Adds tags to an existing run.

    Args:
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.
        tags (list): List of tags to add.

    Returns:
        dict: Updated run data or error message.
    """
    data = run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        run.update_one({"run_id": run_id, "project_name": project_name},
                             {"$push": {"tags": tags}})
        run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/update_status")
def update_status(run_id: str, project_name: str, status: str):
    """
    Updates the status of a specific run.

    Args:
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.
        status (str): New status (e.g., 'completed', 'failed').

    Returns:
        dict: Updated run data or error message.
    """
    data = run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        run.update_one({"run_id": run_id, "project_name": project_name},
                             {"$set": {"status": status.lower()}})
        return run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.post("/{project_name}/runs/{run_id}/add_notes")
def add_notes(run_id: str, project_name: str, notes: str):
    """
    Adds descriptive notes to a specific run.

    Args:
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.
        notes (str): Notes or description about the run.

    Returns:
        dict: Updated run data or error message.
    """
    data = run.find_one({"run_id": run_id, "project_name": project_name})
    if data:
        run.update_one({"run_id": run_id, "project_name": project_name},
                             {"notes": notes})
        return run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST"}

@app.get("/projects/{status}")
def get_projects_from_status(status: str):
    """
    Retrieves all projects with the given status.

    Args:
        status (str): Run status to filter by (e.g., 'completed').

    Returns:
        dict: List of projects with the specified status or a message.
    """
    data = run.find({"status": status.lower()}, {"_id": 0}).to_list()
    if data:
        return {"data":data}

    else:
        return {"message": f"No {status} projects found"}

@app.get("/{project_name}/runs/{run_id}")
def fetch_run_id(run_id: str, project_name: str):
    """
    Retrieves all details associated with a specific run ID.

    Args:
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.

    Returns:
        dict: Run details or error message.
    """
    docs = run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    if docs:
        return docs
    else:
        return {"Error": f"Run_Id : {run_id}, DOESN'T EXIST"}

@app.get("/projects")
def get_all_projects():
    """
    Retrieves a list of all distinct project names.

    Returns:
        list or dict: List of project names or an error message.
    """
    projects = run.distinct("project_name")
    if projects:
        return projects
    else:
        return {"Error": "No, Projects made/saved yet."}

@app.get("/{project_name}/plots/available_metrics")
def get_available_metrics(project_name: str):
    """
    Lists all available metrics logged for a given project.

    Args:
        project_name (str): Name of the project.

    Returns:
        dict: List of available metrics per run.
    """
    metrics = run.find({"project_name": project_name}, {"metrics.metric": 1, "_id": 0, "run_id": 1}).to_list()
    # uniq_metrics = list(set(metrics))    # Getting only the unique metrics.

    return {"all_available_metrics": metrics}

@app.get("/{project_name}/plots/{metric}")
def plot_metrics(metric: str, run_id: str, project_name: str):
    """
    Generates and returns a plot image for a specific metric of a run.

    Args:
        metric (str): Name of the metric (e.g., 'loss').
        run_id (str): Unique identifier of the run.
        project_name (str): Name of the project.

    Returns:
        StreamingResponse or dict: PNG image stream of the plot or error message.
    """

    data = run.find_one({"run_id": run_id, "project_name": project_name, "metrics.metric": metric.lower()})
    if data:
        values = data["metrics"]["details"]
        steps = values["step"]
        iter_values = values["value"]

        plt.figure()
        plt.plot(steps, iter_values)
        plt.xlabel("Step")
        plt.ylabel(metric.title())
        plt.title(f"{metric.title()} plot of Run_id : {run_id}")

        # fig = plt.gcf()
        # return fig, This statement will raise an error as fig is a python object and not a web serializable response, So we need to stream this in the form of binary streams.

        buf = BytesIO()
        plt.savefig(buf, format = "png")
        buf.seek(0)

        return StreamingResponse(buf, media_type = "image/png")

    else:
        return {"Error": f"Run_Id : {run_id} or Project: {project_name} DOESN'T EXIST OR The metrics field DOESN'T EXIST."}

@app.delete("/projects/delete")
def delete_projects(project_name: str, run_id: str = None):
    """
    Deletes a specific run or all runs under a project.

    Args:
        project_name (str): Name of the project.
        run_id (str, optional): Specific run ID to delete.

    Returns:
        dict: Confirmation message of deleted entries.
    """
    if run_id:
        data = run.delete_many({"run_id": run_id, "project_name": project_name})
        return {"deleted": f"{data.deleted_count} files have been deleted."}

    else:
        data = run.delete_many({"project_name": project_name})
        return {"deleted": f"{data.deleted_count} files have been deleted."}

@app.delete("/delete_all")
def delete_all():
    """
    Deletes all run data from the database.

    Returns:
        dict: Message indicating whether deletion was successful.
    """
    db.drop_collection("Run")
    if db.list_collections().to_list():
        return {"error": "Deletion Failed"}
    else:
        return {"message": "The data deleted successfully."}

if __name__ == '__main__':
    uvicorn.run(app, host = '127.0.0.1', port = 8000)