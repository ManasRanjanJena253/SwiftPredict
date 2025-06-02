from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["SwiftPredict"]

# Defining the schema
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["run_id", "created_at", "project_name"],
        "properties": {
            "run_id": {"bsonType": "string"},
            "project_name": {"bsonType": "string"},
            "created_at": {"bsonType": "Date"},
            "tags": {"bsonType": "array",
                     "items": {"bsonType": "string"}
                     },
            "notes": {"bsonType": "string"},
            "params": {"bsonType": "object",
            "required": ["key", "value"],
                       "properties": {
                           "key": {"bsonType": "string"}
                       }},
            "metrics": {"bsonType": "object",    # metrics = {metric: Name of the metric, details: {step:[all the steps], value: [ALl the corresponding values]}
                       "required": ["metric", "details"],
                        "properties": {
                            "metric": {"bsonType": "string"},
                            "details": {"bsonType": "object",
                                       "items": {"bsonType": "object",
                                                 "required": ["step", "value"],
                                                 "properties": {
                                                     "step": {"bsonType": "integer"},
                                                     "value": {"bsonType": "array",
                                                               "items": {"bsonType": "double"}}
                                                 }}}
                        }
                        },
            "status": {"bsonType": "string"}
        }

    }
}

# Creating the "Run" collection
collections = db.list_collection_names()
if "Run" not in collections :
    db.create_collection(name = "Run",
                         validator = validator,
                         warning = "error")
    print("Run Collection Created")

else :
    print("The Run collection already exists")

