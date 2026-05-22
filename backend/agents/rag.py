import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

load_dotenv()

# Configuration
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Initialize embeddings (Local & Free)
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def add_pdf_to_vectorstore(pdf_path, pdf_id):
    """Loads a PDF, splits it, and adds it to Chroma with pdf_id as metadata."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata to each chunk
    for chunk in chunks:
        chunk.metadata["pdf_id"] = str(pdf_id)
        
    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    return True

def get_relevant_context(query, pdf_id, k=3):
    """Retrieves top-k context chunks for a specific PDF."""
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Filter by pdf_id metadata
    results = db.similarity_search(
        query, 
        k=k, 
        filter={"pdf_id": str(pdf_id)}
    )
    
    context = "\n\n".join([doc.page_content for doc in results])
    return context
