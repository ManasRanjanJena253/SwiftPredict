from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Defining the schema
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["run_id", "created_at", "project_name"],
        "properties": {
            "run_id": {"bsonType": "string"},
            "project_name": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "tags": {"bsonType": "array",
                     "items": {"bsonType": "string"}
                     },
            "notes": {"bsonType": "string"},
            "params": {"bsonType": "array",
                       "items": {"bsonType": "object",
                                 "required": ["key", "value"],
                                 "properties": {
                                     "key": {"bsonType": "string"},
                                     "value": {}
                                 }}
                       },
            "metrics": {"bsonType": "object",    # metrics = {metric: Name of the metric, details: {step:[all the steps], value: [ALl the corresponding values]}
                       "required": ["metric", "details"],
                        "properties": {
                            "metric": {"bsonType": "string"},
                            "details": {"bsonType": "object",
                                                 "required": ["step", "value"],
                                                 "properties": {
                                                     "step": {"bsonType": "array",
                                                              "items": {"bsonType": "double"}},
                                                     "value": {"bsonType": "array",
                                                               "items": {"bsonType": "double"}}
                                                 }}}
                        }
                        },
            "status": {"bsonType": "string"}
        }

    }

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["SwiftPredict"]

    collections = await db.list_collection_names()
    if "Run" not in collections:
        await db.create_collection(
            name = "Run",
            validator = validator,
            validationAction = "error"
        )
        print("Run collection created")
    else:
        print("The Run collection already exists")

if __name__ == "__main__":
    asyncio.run(main())

