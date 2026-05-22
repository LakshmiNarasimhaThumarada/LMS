import pymongo
from pymongo import MongoClient
import sys

# This connects to the service currently running on your PC
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    
    # Test if it's working
    client.admin.command('ping')
    print("✨ MongoDB is connected and ready for the LMS!")
    
    # List databases to be sure
    print(f"Databases found: {client.list_database_names()}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n💡 Tip: It looks like the MongoDB service is not started.")
    print("Please run 'net start MongoDB' in a Command Prompt opened as ADMINISTRATOR.")
    sys.exit(1)
