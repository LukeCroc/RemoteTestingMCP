# local_test_server_proxy.py
from flask import Flask, request, jsonify
import subprocess
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask(__name__)

# Your company proxy configuration
PROXIES = {
    'http': 'http://proxy-sin.sicarrier.com:8080',
    'https': 'http://proxy-sin.sicarrier.com:8080'
}

def test_proxy_connectivity():
    """Test if we can reach external services through proxy"""
    try:
        # Test with verify=False to bypass SSL certificate validation
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=PROXIES,
            verify=False,
            timeout=10
        )
        print(f"✅ Proxy connectivity test: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Proxy connectivity failed: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok", 
        "message": "Test server is running",
        "proxy_configured": True
    })

@app.route('/run-test', methods=['POST'])
def run_test():
    try:
        data = request.json
        if not data or 'command' not in data:
            return jsonify({"error": "Missing 'command' in request"}), 400
        
        test_command = data['command']
        working_dir = data.get('working_dir', '.')
        
        # Basic security check
        if any(blocked in test_command for blocked in ['rm ', 'sudo', '>', '|', '&', ';']):
            return jsonify({"error": "Command contains potentially dangerous characters"}), 400
        
        print(f"Executing command: {test_command} in directory: {working_dir}")
        
        # Execute the test command
        result = subprocess.run(
            test_command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        response = {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": test_command
        }
        
        print(f"Command completed with return code: {result.returncode}")
        return jsonify(response)
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Test execution timed out after 30 seconds"}), 408
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Testing proxy connectivity...")
    if test_proxy_connectivity():
        print("✅ Proxy is working! Starting server...")
        print("Starting local test server on http://localhost:5000")
        app.run(host='localhost', port=5000, debug=True)
    else:
        print("❌ Proxy connectivity test failed. Check proxy settings.")





#My company has limited upload net traffic , the proxy only allow non-stream http1.1 request of below 20kb size sent out, block all request sent in.(downloading seem have no limitation)  so I cant make an agent local, because the outwise request exceeds 20kb quickly. I am designing a seperated working flow. The agent and codebase are maintained in github codespace(Agent as RooCode), I communicate with it using my phone. The agent read and write files all in github codespace(or my home computer). The testing is using an MCP tool that uses http request to ask my working local computer to run test cmd and do the test, the result also send back to agent with http to agent. But this wont work because the proxy block all request sent in. Then what do I do?