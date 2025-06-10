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
    return {"Welcome": "SwiftPredict: Your compass from data to discovery."}
@app.post("/{project_name}/runs/{run_id}/log_param")
def log_param(key: str, value, run_id: str, project_name: str):
    """
    Used to log the parameters used when training a certain model.
    :param key: The name of the parameter.
    :param value: The value given/assigned to that parameter.
    :param run_id: The unique run_id of that particular model.
    :param project_name: The name of the project.
    :return: The updated data.
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
    Used to log the metrics used for evaluation of the model.
    :param key: The name of the metric
    :param value: The value of the metric calculated.
    :param run_id: The unique run_id of that particular parameter.
    :param step: The iteration at which the value of the metrics is being given.
    :param project_name: The name of the project.
    :return: The updated data.
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
    Used to add tags to already created runs.
    :param run_id: The unique run_id associated with a run.
    :param project_name: The name of the project.
    :param tags: List of tags you want to provide to a particular run.
    :return: The updated data.
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
    Used to add tags to already created runs.
    :param run_id: The unique run_id associated with a run.
    :param project_name: The name of the project.
    :param status: The current running status of the project.
    :return: The updated data.
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
    Used to add tags to already created runs.
    :param run_id: The unique run_id associated with a run.
    :param project_name: The name of the project.
    :param notes: For experiment description/logging.
    :return: The updated data.
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
    Used to get all the projects which are marked as completed.
    :return:
    """
    data = run.find({"status": status.lower()}, {"_id": 0}).to_list()
    if data:
        return {"data":data}

    else:
        return {"message": f"No {status} projects found"}

@app.get("/{project_name}/runs/{run_id}")
def fetch_run_id(run_id: str, project_name: str):
    """
    Used to fetch all the data associated with a specific run_id .
    :param run_id: The unique run_id of a particular code run.
    :param project_name: The name of the project.
    :return: The updated data.
    """
    docs = run.find_one({"run_id": run_id, "project_name": project_name}, {"_id": 0})
    if docs:
        return docs
    else:
        return {"Error": f"Run_Id : {run_id}, DOESN'T EXIST"}

@app.get("/projects")
def get_all_projects():
    """
    Used to get all distinct projects you have created.
    :return: List of projects.
    """
    projects = run.distinct("project_name")
    if projects:
        return projects
    else:
        return {"Error": "No, Projects made/saved yet."}

@app.get("/{project_name}/plots/available_metrics")
def get_available_metrics(project_name: str):
    """
    Used to get all the metrics which are available for a particular project.
    :param project_name:
    :return: list of all metrics.
    """
    metrics = run.find({"project_name": project_name}, {"metrics.metric": 1, "_id": 0, "run_id": 1}).to_list()
    # uniq_metrics = list(set(metrics))    # Getting only the unique metrics.

    return {"all_available_metrics": metrics}

@app.get("/{project_name}/plots/{metric}")
def plot_metrics(metric: str, run_id: str, project_name: str):
    """
    This function takes in the metric name and a list containing dicts containing each iteration(step) and metric value at that instance.
    :param metric: Name of the metric.
    :param run_id: The unique run_id of a particular code run.
    :param project_name: The name of the project.
    :return: Streaming Image.
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
    Used to delete an all projects with a particular name or projects with a certain run_id
    :param project_name: The name of the project.
    :param run_id: The unique id given to a run.
    :return: Confirmation  json message.
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
    Used to delete all the records of all the projects.
    """
    db.drop_collection("Run")
    if db.list_collections().to_list():
        return {"error": "Deletion Failed"}
    else:
        return {"message": "The data deleted successfully."}

if __name__ == '__main__':
    uvicorn.run(app, host = '127.0.0.1', port = 9000)