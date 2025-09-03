import subprocess
import os

def setup_pat_auth():
    """设置使用Personal Access Token进行GitHub认证"""
    print("=== 设置GitHub Personal Access Token认证 ===")
    
    # 首先检查当前remote URL
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    print("当前remote配置:")
    print(result.stdout)
    
    # 提示用户创建PAT
    print("\n请按照以下步骤操作:")
    print("1. 访问 https://github.com/settings/tokens")
    print("2. 点击 'Generate new token' (classic)")
    print("3. 给token一个描述名称 (如: 'MCP Server Access')")
    print("4. 选择适当的权限 (至少需要 'repo' 权限)")
    print("5. 点击 'Generate token'")
    print("6. 复制生成的token (非常重要！)")
    print("\n然后将remote URL改为包含PAT的形式:")
    print("git remote set-url origin https://[YOUR_USERNAME]:[YOUR_TOKEN]@github.com/LukeCroc/RemoteTestingMCP.git")
    
    # 检查是否已经有PAT配置
    remote_url = result.stdout
    if "https://" in remote_url and "@github.com" in remote_url:
        print("\n✅ 检测到可能已经配置了PAT认证")
    else:
        print("\n⚠️  当前使用的是普通HTTPS认证，可能需要浏览器交互")

def test_network_connectivity():
    """测试网络连接性"""
    print("\n=== 测试网络连接性 ===")
    
    # 测试GitHub连接
    try:
        import requests
        response = requests.get("https://github.com", timeout=10)
        if response.status_code == 200:
            print("✅ GitHub网站访问正常")
            return True
        else:
            print(f"❌ GitHub访问异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 网络连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("GitHub认证配置助手")
    
    network_ok = test_network_connectivity()
    if not network_ok:
        print("\n⚠️  网络连接可能有问题，请检查网络设置")
    
    setup_pat_auth()
    
    print("\n=== 当前Git配置 ===")
    result = subprocess.run("git config --global --list", shell=True, capture_output=True, text=True)
    print(result.stdout)