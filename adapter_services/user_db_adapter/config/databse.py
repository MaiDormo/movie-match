from pymongo import MongoClient
import os
import certifi

# Initialize MongoDB client
atlas_uri = os.getenv("ATLAS_URI", "")
mongo_client_kwargs = {
    "serverSelectionTimeoutMS": 5000,
}

# Atlas/SRV deployments require TLS; provide explicit CA bundle in containerized runtime.
if atlas_uri.startswith("mongodb+srv://") or "mongodb.net" in atlas_uri:
    mongo_client_kwargs.update(
        {
            "tls": True,
            "tlsCAFile": certifi.where(),
        }
    )

mongo_client = MongoClient(atlas_uri, **mongo_client_kwargs)

def get_mongo_client():
    return mongo_client