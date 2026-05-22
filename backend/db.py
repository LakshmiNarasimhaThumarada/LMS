import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/edumind")

def get_db():
    client = MongoClient(MONGO_URI)
    db = client.edumind
    return db

db = get_db()
users_collection = db.users
