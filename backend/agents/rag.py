import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

def get_relevant_context(query, pdf_id, k=4):
    """Retrieves top-k context chunks for a specific PDF, with smart summary detection."""
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Check if the user is asking for a summary/overview of the document
    summary_keywords = ["summarize", "summary", "overview", "synopsis", "what is this", "what is the document", "about"]
    is_summary_request = any(keyword in query.lower() for keyword in summary_keywords)
    
    if is_summary_request:
        try:
            # Retrieve all chunks for this PDF to extract the beginning of the file (introduction/abstract)
            all_data = db.get(where={"pdf_id": str(pdf_id)})
            documents = all_data.get("documents", [])
            metadatas = all_data.get("metadatas", [])
            
            if documents:
                # Pair documents and metadata, and sort by page number
                paired_docs = list(zip(documents, metadatas))
                paired_docs.sort(key=lambda x: x[1].get("page", 0))
                
                # Take the first k chunks representing the introduction/start of the PDF
                selected_docs = paired_docs[:k]
                context = "\n\n".join([doc[0] for doc in selected_docs])
                if context.strip():
                    return context
        except Exception as e:
            print(f"Error fetching summary chunks: {e}")
            
    # Fallback to standard semantic similarity search
    results = db.similarity_search(
        query, 
        k=k, 
        filter={"pdf_id": str(pdf_id)}
    )
    
    context = "\n\n".join([doc.page_content for doc in results])
    return context
