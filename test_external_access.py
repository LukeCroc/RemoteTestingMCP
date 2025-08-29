# test_external_access.py
import socket
import requests

def test_external_access():
    print("Testing external access possibilities...")
    
    # Get your public IP
    try:
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"Your public IP: {public_ip}")
    except:
        print("Could not determine public IP")
    
    # Test if port 5000 is open from outside
    print("\nTesting port 5000 accessibility (this will likely fail):")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((public_ip, 5000))
        if result == 0:
            print("✅ Port 5000 is open! (This is surprising)")
        else:
            print("❌ Port 5000 is closed (expected)")
        sock.close()
    except Exception as e:
        print(f"❌ Port test failed: {e}")
    
    print("\n" + "="*50)
    print("CONCLUSION: Your corporate firewall likely blocks")
    print("incoming connections. You'll need a tunnel solution.")
    print("="*50)

if __name__ == "__main__":
    test_external_access()