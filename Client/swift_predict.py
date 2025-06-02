# Importing dependencies
from Backend.app.api.logging import log_param, log_metric
import uuid
from Backend.app.core.config import db
from datetime import datetime

run = db["Run"]

class SwiftPredict :
    def __init__(self, project_name, api_base="http://localhost:8000"):
        self.run_id = str(uuid.uuid4())
        self.api_base = api_base
        self.project_name = project_name
        self.created_at = datetime.now()

    async def log_param(self, key, value):
        param = {"run_id": self.run_id, "key": key, "value": value,
                 "created_at": self.created_at, "project_name": self.project_name}
        await run.insert_one(param)

    async def log_metric(self, step, key, value):
        metric = {"step": step, "value": value}
        await run.update_one({"run_id": self.run_id, "key": key, "project_name": self.project_name},
                             {"$push": {"items": metric}})  # Appending the steps into the array of metrics, to create a time series data to plot more easily.

    async def log_params(self, params: dict):
        for key, value in params.items():
            await self.log_param(key = key, value = value)

    async def log_metrics(self, metrics: dict):
        for key, value in metrics.items():
            await self.log_metric(key = key, value = value)

    async def find_project_runs(self):
        return await run.find({"project_name": self.project_name})

    async def finalize_run(self, status: str, notes: str = '', tags: list = None):
        await run.update_one({"run_id": self.run_id},
                             {"$set": {
                                 "status": status,
                                 "notes": notes,
                                 "tags": tags or []
                             }})
