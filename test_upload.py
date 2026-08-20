import os
import requests
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(load_dotenv_path)

JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_edumind_key_2025")
JWT_ALGORITHM = "HS256"

# Create a valid token
token_payload = {
    "id": "60d5ecb863a34f2d78b87123", # valid dummy object id
    "email": "test@student.com",
    "role": "student",
    "exp": datetime.utcnow() + timedelta(days=1)
}
token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Find the user's PDF
uploads_dir = os.path.join(os.path.dirname(__file__), "backend", "uploads")
pdf_file = None
if os.path.exists(uploads_dir):
    for f in os.listdir(uploads_dir):
        if "fagro" in f and f.endswith(".pdf"):
            pdf_file = f
            break

if not pdf_file:
    print("Could not find fagro pdf in backend/uploads!")
    exit(1)

pdf_path = os.path.join(uploads_dir, pdf_file)
print(f"Testing upload of {pdf_file} (size: {os.path.getsize(pdf_path)} bytes)...")

url = "http://127.0.0.1:8000/api/planner/analyze-pdf?pdf_id=dummy_pdf_id_123"
headers = {"Authorization": f"Bearer {token}"}
with open(pdf_path, "rb") as f:
    files = {"file": (pdf_file, f.read(), "application/pdf")}

try:
    print("Sending POST request to FastAPI /api/planner/analyze-pdf...")
    response = requests.post(url, files=files, headers=headers, timeout=120)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
