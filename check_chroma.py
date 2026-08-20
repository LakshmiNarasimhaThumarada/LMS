import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

print("Loading HuggingFace Embeddings...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

if not os.path.exists(CHROMA_PATH):
    print(f"Chroma database path '{CHROMA_PATH}' does not exist!")
else:
    print("Connecting to Chroma DB...")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    try:
        # Get all entries from Chroma
        data = db.get()
        metadatas = data.get("metadatas", [])
        
        pdf_ids = set()
        for meta in metadatas:
            if "pdf_id" in meta:
                pdf_ids.add(meta["pdf_id"])
        
        print("\nSuccessfully connected to Chroma DB.")
        print(f"Total chunk count in vector database: {len(metadatas)}")
        print(f"Indexed PDF IDs: {list(pdf_ids)}")
    except Exception as e:
        print(f"Error querying Chroma DB: {e}")
