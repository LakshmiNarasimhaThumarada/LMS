import os
import pymongo
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

mongo_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/edumind")
client = pymongo.MongoClient(mongo_uri)
db = client.get_database()

CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

print("Loading HuggingFace Embeddings...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
chroma_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

# Get already indexed IDs in Chroma
try:
    data = chroma_db.get()
    indexed_ids = set(meta.get("pdf_id") for meta in data.get("metadatas", []) if "pdf_id" in meta)
    print("Currently indexed Chroma IDs:", list(indexed_ids))
except Exception as e:
    indexed_ids = set()
    print("Error reading Chroma:", e)

from backend.agents.rag import add_pdf_to_vectorstore

try:
    analyses = list(db.pdf_analysis.find({}))
    print(f"\nFound {len(analyses)} PDF records in MongoDB.")
    
    for record in analyses:
        pdf_id = str(record["_id"])
        filename = record.get("filename", "Unknown")
        file_path = record.get("file_path")
        
        # If the ID is a dummy or already indexed, skip it
        if pdf_id == "dummy_pdf_id_123":
            continue
            
        if pdf_id in indexed_ids:
            print(f"- '{filename}' ({pdf_id}) is already indexed.")
            continue
            
        # Resolve active file path
        active_path = None
        paths_to_try = [
            file_path,
            os.path.join("backend", file_path) if file_path else None,
            os.path.join("c:\\Users\\Dell\\OneDrive\\Desktop\\LMS_PROJECT", file_path) if file_path else None
        ]
        
        for p in paths_to_try:
            if p and os.path.exists(p):
                active_path = p
                break
                
        if not active_path:
            print(f"- File for '{filename}' ({pdf_id}) not found on disk. Skipping.")
            continue
            
        print(f"- Indexing '{filename}' ({pdf_id}) from {active_path}...")
        try:
            success = add_pdf_to_vectorstore(active_path, pdf_id)
            print(f"  Result: Success={success}")
        except Exception as err:
            print(f"  Result: FAILED: {err}")
            
except Exception as e:
    print("Error querying MongoDB:", e)
