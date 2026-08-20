import os
import sys

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.agents.rag import add_pdf_to_vectorstore

pdf_file = "backend/uploads/1787049573218-fagro-8-1767878.pdf"
pdf_id = "dummy_pdf_id_123"

print(f"Testing local embedding of {pdf_file}...")
try:
    success = add_pdf_to_vectorstore(pdf_file, pdf_id)
    print(f"Embedding success: {success}")
except Exception as e:
    import traceback
    traceback.print_exc()
