import requests

def check_port(port):
    url = f"http://127.0.0.1:{port}/health"
    try:
        response = requests.get(url, timeout=2)
        print(f"Port {port}: REACHABLE (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"Port {port}: NOT REACHABLE")
        return False
    except Exception as e:
        print(f"Port {port}: ERROR ({type(e).__name__})")
        return False

print("Checking backend ports...")
check_port(5000)
check_port(6000)
