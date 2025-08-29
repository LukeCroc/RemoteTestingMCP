# test_client_proxy.py
import requests
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Your company proxy configuration
PROXIES = {
    'http': 'http://proxy-sin.sicarrier.com:8080',
    'https': 'http://proxy-sin.sicarrier.com:8080'
}

class ProxyTestClient:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.session = requests.Session()
        # Configure session to use company proxy and ignore SSL errors
        self.session.proxies = PROXIES
        self.session.verify = False
    
    def health_check(self):
        """Check if local server is reachable"""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
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
                timeout=30
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection failed: {str(e)}"}
    
    def test_external_connectivity(self):
        """Test if we can reach external services"""
        test_urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/get",
            "https://api.github.com"
        ]
        
        print("Testing external connectivity through proxy...")
        for url in test_urls:
            try:
                response = self.session.get(url, timeout=10)
                print(f"✅ {url}: {response.status_code}")
            except Exception as e:
                print(f"❌ {url}: {e}")

def run_comprehensive_test():
    client = ProxyTestClient()
    
    print("=== Testing External Connectivity ===")
    client.test_external_connectivity()
    
    print("\n=== Testing Local Server Connection ===")
    
    # Test local server health
    print("\n1. Testing server health...")
    health = client.health_check()
    print("Health response:", json.dumps(health, indent=2))
    
    if "error" in health:
        print("❌ Cannot reach local server. This is expected due to corporate firewall.")
        print("The proxy allows outbound traffic but blocks inbound connections.")
        return False
    
    # If we get here, the local connection works (unlikely in corporate env)
    print("\n2. Testing basic commands...")
    result = client.run_test("python --version")
    print("Result:", json.dumps(result, indent=2))
    
    return True

if __name__ == "__main__":
    run_comprehensive_test()