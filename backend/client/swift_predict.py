# Importing dependencies
import secrets
from datetime import datetime
from pymongo import MongoClient


class SwiftPredict :
    def __init__(self, project_name, api_base="http://localhost:8000"):
        self.run_id = str(secrets.token_hex(2))
        self.api_base = api_base
        self.project_name = project_name
        self.created_at = datetime.now()
        self.client = MongoClient(host = "localhost", port = 27017)
        self.db = self.client["SwiftPredict"]
        self.run = self.db["Run"]

    def log_param(self, key: str, value):
        check = self.run.find_one({"run_id": self.run_id})
        if check:
            self.run.update_one({"run_id": self.run_id},
                                      {"$set": {"project_name": self.project_name,"created_at": self.created_at},
                                  "$push": {"params": {"key": key, "value": value}}})
        else :
            param = {"run_id": self.run_id, "params": [{"key": key, "value": value}], "created_at": self.created_at,
                     "project_name": self.project_name}
            self.run.insert_one(param)

    def log_metric(self, step, key: str, value):
        check = self.run.find_one({"run_id": self.run_id})
        if check :
            self.run.update_one({"run_id": self.run_id, "project_name": self.project_name},
                                      {"$set": {"metrics.metric": key.lower()},
                                  "$push": {"metrics.details.step": float(step), "metrics.details.value": float(value)}})
        else:
            self.run.insert_one({
                "run_id": self.run_id,
                "project_name": self.project_name,
                "metrics": {
                    "metric": key,
                    "details": {
                        "step": [float(step)],
                        "value": [float(value)]
                    }
                },
                "created_at": self.created_at
            })

    def log_params(self, params: dict):
        for key, value in params.items():
            self.log_param(key = key, value = value)

    def find_project_runs(self):
        return self.run.find_one({"project_name": self.project_name})

    def finalize_run(self, status: str, notes: str = '', tags: list = None):
        self.run.update_one({"run_id": self.run_id},
                                  {"$set": {
                                 "status": status,
                                 "notes": notes,
                                 "tags": tags or []
                             }})
