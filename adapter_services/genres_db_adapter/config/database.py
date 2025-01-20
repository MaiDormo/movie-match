from pymongo import MongoClient
import os

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv("ATLAS_URI"))

def get_mongo_client():
    return mongo_client