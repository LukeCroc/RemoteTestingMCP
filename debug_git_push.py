import subprocess
import os
import json
import uuid
import time

def debug_git_push():
    """详细调试git push问题，模拟MCP服务器的确切行为"""
    print("=== 开始调试git push问题 ===")
    
    # 模拟MCP服务器的行为
    job_id = str(uuid.uuid4())
    job_data = {
        "status": "pending",
        "job": {
            "id": job_id,
            "command": "echo Hello World 101!"
        },
        "result": {
            "stdout": None,
            "stderr": None,
            "return_code": None
        }
    }
    
    # 写入文件（和MCP服务器完全一样）
    with open("remote_job.json", 'w') as f:
        json.dump(job_data, f, indent=2)
    print(f"✅ 已修改 remote_job.json，Job ID: {job_id}")
    
    # 测试每个git命令，使用和MCP服务器相同的参数
    print("\n=== 测试git add ===")
    try:
        result = subprocess.run("git add remote_job.json", shell=True, capture_output=True, text=True, check=True)
        print(f"✅ git add 成功 - 退出码: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"❌ git add 失败: {e}")
        print(f"stderr: {e.stderr}")
        print(f"stdout: {e.stdout}")
        return
    
    print("\n=== 测试git commit ===")
    try:
        commit_message = f"Add remote test job {job_id}"
        result = subprocess.run(f'git commit -m "{commit_message}"', shell=True, capture_output=True, text=True, check=True)
        print(f"✅ git commit 成功 - 退出码: {result.returncode}")
        print(f"输出: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ git commit 失败: {e}")
        print(f"stderr: {e.stderr}")
        print(f"stdout: {e.stdout}")
        return
    
    print("\n=== 测试git push ===")
    try:
        # 使用和MCP服务器完全相同的命令
        result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True, check=True)
        print(f"✅ git push 成功 - 退出码: {result.returncode}")
        if result.stdout:
            print(f"输出: {result.stdout.strip()}")
        if result.stderr:
            print(f"错误输出: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ git push 失败: {e}")
        print(f"stderr: {e.stderr}")
        print(f"stdout: {e.stdout}")
        print("\n=== 详细错误分析 ===")
        print("可能的原因:")
        print("1. 认证问题 - 检查git凭据")
        print("2. 网络连接问题")
        print("3. 分支权限问题")
        print("4. 防火墙或代理设置")
        
        # 测试网络连接
        print("\n=== 测试GitHub连接 ===")
        try:
            ping_result = subprocess.run("ping github.com -n 2", shell=True, capture_output=True, text=True)
            if ping_result.returncode == 0:
                print("✅ GitHub网络连接正常")
            else:
                print("❌ GitHub网络连接失败")
        except Exception as ping_error:
            print(f"网络测试失败: {ping_error}")

if __name__ == "__main__":
    debug_git_push()