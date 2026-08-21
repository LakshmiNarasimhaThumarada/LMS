import os
import pymongo
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

mongo_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/edumind")
client = pymongo.MongoClient(mongo_uri)
db = client.get_database()

print("Connected to MongoDB:", db.name)
try:
    # Check "pdfs" collection (Node.js)
    pdfs = list(db.pdfs.find({}))
    print(f"Total PDFs in collection 'pdfs': {len(pdfs)}")
    for p in pdfs:
        print(f"- Filename: {p.get('filename')}, ID: {str(p.get('_id'))}")
        
    # Check "pdf_analysis" collection (FastAPI)
    pdf_analyses = list(db.pdf_analysis.find({}))
    print(f"\nTotal PDF Analyses in collection 'pdf_analysis': {len(pdf_analyses)}")
    for pa in pdf_analyses:
        print(f"- Filename: {pa.get('filename')}, ID: {str(pa.get('_id'))}")
except Exception as e:
    print(f"Error querying MongoDB: {e}")
