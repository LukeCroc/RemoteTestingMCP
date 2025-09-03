"""
修复版的MCP服务器，解决git push问题
"""
from mcp.server.fastmcp import FastMCP
import time
import json
import os
import subprocess
import uuid
from typing import Optional, Dict, Any

# Create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def remote_test(project_root: str, command: str) -> Dict[str, Any]:
    """Run a remote test and waiting for completion. The remote commands run in a Windows powershell.
    
    Args:
        project_root: Absolute path to the project root directory， for modifying files and git commands
        command: Command to execute remotely (use PowerShell syntax with semicolons, e.g., 'cd subdir; command', all subdir using relative dir)
        
    Returns:
        Dictionary containing the test results
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job data structure
    job_data = {
        "status": "pending",
        "job": {
            "id": job_id,
            "command": command
        },
        "result": {
            "stdout": None,
            "stderr": None,
            "return_code": None
        }
    }
    
    # Write to remote_job.json in the specified project root directory
    job_file_path = os.path.join(project_root, "remote_job.json")
    
    try:
        with open(job_file_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        print(f"Job {job_id} created at {job_file_path}")
        
        # Commit and push to GitHub so the poller can detect the job
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_root)
            
            # Git add and commit only the job file
            # 修复：不使用capture_output，允许交互式认证
            subprocess.run("git add remote_job.json", shell=True, check=True)
            subprocess.run(f'git commit -m "Add remote test job {job_id}"', shell=True, check=True)
            
            # 修复：git push使用更好的错误处理和重试机制
            push_success = False
            max_push_attempts = 3
            
            for attempt in range(max_push_attempts):
                try:
                    print(f"尝试git push (尝试 {attempt + 1}/{max_push_attempts})...")
                    # 不使用capture_output，允许看到认证提示
                    result = subprocess.run("git push origin main", shell=True, check=True)
                    push_success = True
                    print(f"✅ git push 成功")
                    break
                except subprocess.CalledProcessError as e:
                    print(f"❌ git push 失败 (尝试 {attempt + 1}): {e}")
                    if attempt < max_push_attempts - 1:
                        print(f"等待5秒后重试...")
                        time.sleep(5)
                    else:
                        print("所有git push尝试都失败了，继续轮询")
            
            # Restore original working directory
            os.chdir(original_cwd)
            
        except subprocess.CalledProcessError as e:
            print(f"Git operations failed: {e}")
            # Continue with polling even if git push fails
        
        # Wait for job completion (polling)
        max_attempts = 60  # 5 minutes at 5 second intervals
        for attempt in range(max_attempts):
            time.sleep(5)  # Wait 5 seconds between checks
            
            try:
                with open(job_file_path, 'r') as f:
                    current_data = json.load(f)
                
                if current_data.get("status") == "completed":
                    return {
                        "job_id": job_id,
                        "status": "completed",
                        "result": current_data["result"]
                    }
                    
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        return {
            "job_id": job_id,
            "status": "timeout",
            "error": "Job timed out after 5 minutes"
        }
        
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "error",
            "error": f"Failed to create job file: {str(e)}"
        }

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()