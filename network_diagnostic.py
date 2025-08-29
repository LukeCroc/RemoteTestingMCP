# test_inbound_connectivity.py
import socket
import requests

def test_inbound_connections():
    print("Testing if external connections can reach this machine...")
    
    # Test 1: Check if port 5000 is accessible from outside
    try:
        # Try to connect to a public service that echoes your IP
        response = requests.get('https://httpbin.org/ip', timeout=10)
        your_ip = response.json()['origin'].split(',')[0]
        print(f"Your public IP: {your_ip}")
        
        # Now check if that IP can accept connections on port 5000
        # (This will likely fail due to corporate firewall)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((your_ip, 5000))
        
        if result == 0:
            print("✅ Port 5000 is accessible from outside!")
        else:
            print("❌ Port 5000 is NOT accessible from outside (corporate firewall)")
            
    except Exception as e:
        print(f"Error testing connectivity: {e}")

if __name__ == "__main__":
    test_inbound_connections()