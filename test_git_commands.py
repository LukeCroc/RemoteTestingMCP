import subprocess
import os
import json
import uuid

def test_git_commands():
    """测试 Git 命令是否正常工作（模拟 MCP 服务器行为）"""
    print("测试 Git 命令执行（模拟 MCP 服务器）...")
    
    # 模拟 MCP 服务器的行为：先修改 remote_job.json
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
    
    # 写入文件
    with open("remote_job.json", 'w') as f:
        json.dump(job_data, f, indent=2)
    print(f"已修改 remote_job.json，Job ID: {job_id}")
    
    # 测试 git status
    try:
        result = subprocess.run("git status", shell=True, capture_output=True, text=True)
        print(f"git status 退出码: {result.returncode}")
        print(f"git status 输出: {result.stdout}")
    except Exception as e:
        print(f"git status 执行失败: {e}")
        return
    
    # 测试 git add
    try:
        result = subprocess.run("git add remote_job.json", shell=True, capture_output=True, text=True)
        print(f"git add 退出码: {result.returncode}")
        if result.stderr:
            print(f"git add 错误: {result.stderr}")
    except Exception as e:
        print(f"git add 执行失败: {e}")
        return
    
    # 测试 git commit
    try:
        commit_message = f"Test commit for job {job_id}"
        result = subprocess.run(f'git commit -m "{commit_message}"', shell=True, capture_output=True, text=True)
        print(f"git commit 退出码: {result.returncode}")
        print(f"git commit 输出: {result.stdout}")
        if result.stderr:
            print(f"git commit 错误: {result.stderr}")
    except Exception as e:
        print(f"git commit 执行失败: {e}")
        return
    
    # 测试 git push（但可能因为网络问题失败）
    try:
        result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
        print(f"git push 退出码: {result.returncode}")
        if result.stdout:
            print(f"git push 输出: {result.stdout}")
        if result.stderr:
            print(f"git push 错误: {result.stderr}")
    except Exception as e:
        print(f"git push 执行失败: {e}")

if __name__ == "__main__":
    test_git_commands()