import requests
import sys

def check_backend(url="http://127.0.0.1:6000"):
    print(f"🔍 Testing connection to: {url}")
    try:
        # 1. Test basic connectivity (Health Check)
        print("--- Step 1: Health Check ---")
        response = requests.get(f"{url}/health", timeout=5)
        print(f"✅ Connection Successful!")
        print(f"Response (Status {response.status_code}): {response.json()}")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Failed: Could not reach the server on {url}.")
        print("Check if you have run: python app.py inside the backend folder.")
        if "10051" in str(e) or "10054" in str(e):
            print("This usually means something on your network (Firewall/Antivirus) or another process is blocking the connection.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:6000"
    check_backend(url)
