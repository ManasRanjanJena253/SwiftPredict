# Importing dependencies
import secrets
from datetime import datetime
import nest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from asgiref.sync import async_to_sync   # Validator to automatically convert async to sync instead of using async run or any other method when using these in other scripts.

nest_asyncio.apply()

class SwiftPredict :
    def __init__(self, project_name, api_base="http://localhost:8000"):
        self.run_id = str(secrets.token_hex(2))
        self.api_base = api_base
        self.project_name = project_name
        self.created_at = datetime.now()
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client["SwiftPredict"]
        self.run = self.db["Run"]

    @async_to_sync()
    async def log_param(self, key: str, value):
        check = await self.run.find_one({"run_id": self.run_id})
        if check:
            await self.run.update_one({"run_id": self.run_id},
                                      {"$set": {"project_name": self.project_name,"created_at": self.created_at},
                                  "$push": {"params": {"key": key, "value": value}}})
        else :
            param = {"run_id": self.run_id, "params": [{"key": key, "value": value}], "created_at": self.created_at,
                     "project_name": self.project_name}
            await self.run.insert_one(param)

    @async_to_sync()
    async def log_metric(self, step, key: str, value):
        check = await self.run.find_one({"run_id": self.run_id})
        if check :
            await self.run.update_one({"run_id": self.run_id, "project_name": self.project_name},
                                      {"$set": {"metrics.metric": key.lower()},
                                  "$push": {"metrics.details.step": float(step), "metrics.details.value": float(value)}})
        else:
            await self.run.insert_one({
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

    @async_to_sync()
    async def log_params(self, params: dict):
        for key, value in params.items():
            await self.log_param(key = key, value = value)

    @async_to_sync()
    async def find_project_runs(self):
        return await self.run.find_one({"project_name": self.project_name})

    @async_to_sync()
    async def finalize_run(self, status: str, notes: str = '', tags: list = None):
        await self.run.update_one({"run_id": self.run_id},
                                  {"$set": {
                                 "status": status,
                                 "notes": notes,
                                 "tags": tags or []
                             }})
