from pymongo import MongoClient
import mongo_config

client = MongoClient(mongo_config.URI)

def create_user_validator():
    db = client.users_commit_hashes

    user_validator = {
        "$jsonSchema":{
            "bsonType": "object",
            "required": ["user_email", "user_name", "rules"],
            "properties":{
                "user_email": {
                    "bsonType": "string",
                    "description": "must be string and is required"
                },
                "user_name":{
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "rules":{
                        "bsonType": "array",
                        "items":{
                            "bsonType": "object",
                            "properties": {
                                "name":{
                                    "bsonType": "string",
                                    "description": "must be string"
                                },
                                "commit_hashes":{
                                    "bsonType": "array",
                                    "items":{
                                        "bsonType": "object",
                                        "properties": {
                                            "hash": {
                                                "bsonType": "string",
                                                "description": "must be string"
                                            },
                                            "date": {
                                                "bsonType": "string",
                                                "description": "must be string"
                                            },
                                            "status": {
                                                "bsonType": "string",
                                                "description": "must be string"
                                            }
                                        },
                                    },
                                }
                            },
                        }
                    },
                }
            },
        }

    try:
        db.create_collection("users")
    except Exception as e:
        print(e)

    db.command("collMod", "users", validator=user_validator)

create_user_validator()