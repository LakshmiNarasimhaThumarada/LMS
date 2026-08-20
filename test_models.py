import os
from groq import Groq
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    print(f"API Key found: {api_key[:10]}...{api_key[-10:]}")
else:
    print("API Key NOT found in environment!")

client = Groq(api_key=api_key)

try:
    models = client.models.list()
    print("\nAvailable Groq Models on your account:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"\nError listing models: {e}")
