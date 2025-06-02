from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["SwiftPredict"]

# Defining the schema
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["run_id", "created_at", "project_name"],
        "properties": {
            "run_id": {"bsonType": "int"},
            "project_name": {"bsonType": "string"},
            "created_at": {"bsonType": "Date"},
            "tags": {"bsonType": "array",
                     "items": {"bsonType": "string"}
                     },
            "notes": {"bsonType": "string"},
            "params": {"bsonType": "object"},
            "metrics": {"bsonType": "array",
                        "items": {"bsonType": "object"}
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

