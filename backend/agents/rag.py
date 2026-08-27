import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

# Configuration
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize cloud embeddings (Uses 0 MB of local RAM)
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or "hf_dummy_token_for_validation"
embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=hf_token,
    model_name=EMBEDDING_MODEL,
    api_url=f"https://router.huggingface.co/models/{EMBEDDING_MODEL}"
)

# Detect if we should use Pinecone (cloud) or local Chroma
USE_PINECONE = os.getenv("PINECONE_API_KEY") is not None

if USE_PINECONE:
    from langchain_pinecone import PineconeVectorStore
    
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")
    
    def get_vectorstore():
        index_name = "edumind-index"
        return PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=PINECONE_API_KEY
        )
else:
    from langchain_community.vectorstores import Chroma
    def get_vectorstore():
        return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

def add_pdf_to_vectorstore(pdf_path, pdf_id):
    """Loads a PDF, splits it, and adds it to the active vectorstore."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata to each chunk
    for chunk in chunks:
        chunk.metadata["pdf_id"] = str(pdf_id)
        
    if USE_PINECONE:
        db = get_vectorstore()
        db.add_documents(chunks)
    else:
        from langchain_community.vectorstores import Chroma
        Chroma.from_documents(
            chunks, 
            embeddings, 
            persist_directory=CHROMA_PATH
        )
    return True

def get_relevant_context(query, pdf_id, k=4):
    """Retrieves top-k context chunks for a specific PDF, with smart summary detection."""
    db = get_vectorstore()
    
    # Check if the user is asking for a summary/overview of the document
    summary_keywords = ["summarize", "summary", "overview", "synopsis", "what is this", "what is the document", "about"]
    is_summary_request = any(keyword in query.lower() for keyword in summary_keywords)
    
    if is_summary_request:
        try:
            if USE_PINECONE:
                # Semantic search for summary overview
                results = db.similarity_search(
                    "introduction overview summary", 
                    k=k, 
                    filter={"pdf_id": str(pdf_id)}
                )
                context = "\n\n".join([doc.page_content for doc in results])
                if context.strip():
                    return context
            else:
                # Local Chroma support
                all_data = db.get(where={"pdf_id": str(pdf_id)})
                documents = all_data.get("documents", [])
                metadatas = all_data.get("metadatas", [])
                
                if documents:
                    paired_docs = list(zip(documents, metadatas))
                    paired_docs.sort(key=lambda x: x[1].get("page", 0))
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
