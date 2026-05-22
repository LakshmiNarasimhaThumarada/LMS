import fitz  # PyMuPDF is imported as fitz
from typing import List, Dict

def extract_pdf_text(pdf_path: str) -> str:
    """Extract all text from PDF file"""
    
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()
        
        doc.close()
        return text
        
    except Exception as e:
        raise Exception(f"Failed to extract PDF text: {str(e)}")

def detect_page_count(pdf_path: str) -> int:
    """Get total page count"""
    
    try:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
        
    except Exception as e:
        raise Exception(f"Failed to count pages: {str(e)}")

def extract_pdf_metadata(pdf_path: str) -> dict:
    """Extract PDF metadata"""
    
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'pages': detect_page_count(pdf_path)
        }
        
    except Exception as e:
        return {}
