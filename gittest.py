# 这是一个GitHub Codespace上的Git测试文件
# test_client.py (in GitHub Codespace)
import requests
import json

class SimpleTestClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.session = requests.Session()
        # Add timeout to prevent hanging
        self.timeout = 60
    
    def health_check(self):
        """Check if local server is reachable"""
        try:
            response = self.session.get(
                f"{self.server_url}/health",
                timeout=10
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection failed: {str(e)}"}
    
    def run_test(self, test_command, working_dir="."):
        """Send test command to local server"""
        payload = {
            "command": test_command,
            "working_dir": working_dir
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/run-test",
                json=payload,
                timeout=self.timeout
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection failed: {str(e)}"}

# Quick test function
def test_connection():
    # Replace with your local computer's IP address
    LOCAL_SERVER = "http://YOUR_LOCAL_IP:5000"
    
    client = SimpleTestClient(LOCAL_SERVER)
    
    # Test connection
    print("Testing connection to local server...")
    health = client.health_check()
    print("Health check:", health)
    
    # Run a simple test command
    if "error" not in health:
        print("\nRunning simple test command...")
        result = client.run_test("python --version")
        print("Test result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    test_connection()
