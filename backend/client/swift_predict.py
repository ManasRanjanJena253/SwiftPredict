# Importing dependencies
import secrets
from datetime import datetime
from pymongo import MongoClient


class SwiftPredict :
    """
    A lightweight experiment tracking class for logging parameters, metrics, and run metadata
    to a MongoDB backend.

    Attributes:
        run_id (str): A unique identifier for the current run.
        api_base (str): The base URL for the FastAPI server (default is localhost).
        project_name (str): Name of the ML project or experiment.
        created_at (datetime): Timestamp when the run was created.
        client (MongoClient): MongoDB client instance.
        db (Database): MongoDB database named 'SwiftPredict'.
        run (Collection): MongoDB collection for storing run-related data.
    """

    def __init__(self, project_name, api_base="http://localhost:8000"):
        """
           Initializes a new SwiftPredict run instance.

           Args:
               project_name (str): The name of the project for which the run is being logged.
               api_base (str, optional): Base URL of the FastAPI backend. Defaults to 'http://localhost:8000'.
           """
        self.run_id = str(secrets.token_hex(2))
        self.api_base = api_base
        self.project_name = project_name
        self.created_at = datetime.now()
        self.client = MongoClient(host = "localhost", port = 27017)
        self.db = self.client["SwiftPredict"]
        self.run = self.db["Run"]

    def log_param(self, key: str, value):
        """
           Logs a single parameter to the current run in the database.

           Args:
               key (str): The name of the parameter.
               value (Any): The value of the parameter.

           Notes:
               - If the run already exists, the parameter is appended to the list.
               - If the run does not exist, a new document is created with the parameter.
           """
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
        """
        Logs a single metric at a specific step in the run.

        Args:
            step (int or float): The training step, epoch, or iteration.
            key (str): The name of the metric (e.g., 'accuracy', 'loss').
            value (float): The value of the metric at the given step.

        Notes:
            - If metric key already exists, new step and value are appended to lists.
            - If not, a new metrics document is created.
        """
        check = self.run.find_one({"run_id": self.run_id, "metrics.metric": key.lower(), "project_name": self.project_name})
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
        """
         Logs multiple parameters to the current run.

         Args:
             params (dict): A dictionary of key-value pairs representing parameters.

         Example:
             params = {"learning_rate": 0.01, "epochs": 100}
         """
        for key, value in params.items():
            self.log_param(key = key, value = value)

    def find_project_runs(self):
        """
          Retrieves a single run record for the current project.

          Returns:
              dict or None: A document representing the project run if found, else None.

          Notes:
              - Only returns one document. For multiple runs, extend with pagination or aggregation.
          """
        return self.run.find_one({"project_name": self.project_name})

    def finalize_run(self, status: str, notes: str = '', tags: list = None):
        """
          Finalizes the run by setting the status, notes, and optional tags.

          Args:
              status (str): The final status of the run (e.g., 'completed', 'failed').
              notes (str, optional): Additional notes about the run. Defaults to empty string.
              tags (list, optional): List of tags or labels associated with the run. Defaults to None.

          Notes:
              - This helps track run outcomes and categorize runs post-training.
          """
        self.run.update_one({"run_id": self.run_id},
                                  {"$set": {
                                 "status": status,
                                 "notes": notes,
                                 "tags": tags or []
                             }})
