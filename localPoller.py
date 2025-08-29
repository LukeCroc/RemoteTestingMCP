import os
import json
import subprocess
import time
from pathlib import Path

# Configuration
REPO_DIR = "E:/RemoteTestingMCP"  # Update this path
JOB_FILE = Path(REPO_DIR) / "remote_job.json"
POLL_INTERVAL = 30  # seconds

def run_git_command(args):
    """Run git commands in the repo directory."""
    return subprocess.run(["git"] + args, cwd=REPO_DIR, 
                         capture_output=True, text=True)

def check_for_remote_changes():
    """Check if there are changes on the remote repository."""
    # Fetch updates
    run_git_command(["fetch", "origin"])
    
    # Check if local is behind remote
    result = run_git_command(["rev-list", "--count", "HEAD..origin/main"])
    return result.returncode == 0 and int(result.stdout.strip()) > 0

def process_job():
    """Process the job if one exists."""
    # Load the job file
    with open(JOB_FILE, 'r') as f:
        job_data = json.load(f)
    
    # Check if there's a pending job
    if job_data["status"] != "pending":
        return False
    
    # Update status to processing
    job_data["status"] = "processing"
    with open(JOB_FILE, 'w') as f:
        json.dump(job_data, f, indent=2)
    
    run_git_command(["add", "remote_job.json"])
    run_git_command(["commit", "-m", "Started processing job"])
    run_git_command(["push", "origin", "main"])
    
    try:
        # Execute the command
        command = job_data["job"]["command"]
        print(f"Executing: {command}")
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Update with results
        job_data["status"] = "completed"
        job_data["result"] = {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode
        }
        
        with open(JOB_FILE, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        # Push results
        run_git_command(["add", "remote_job.json"])
        run_git_command(["commit", "-m", f"Completed job {job_data['job']['id']}"])
        run_git_command(["push", "origin", "main"])
        
        print(f"Job {job_data['job']['id']} completed successfully")
        return True
        
    except Exception as e:
        # Update with error
        job_data["status"] = "error"
        job_data["result"] = {
            "stdout": "",
            "stderr": str(e),
            "return_code": 1
        }
        
        with open(JOB_FILE, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        run_git_command(["add", "remote_job.json"])
        run_git_command(["commit", "-m", f"Error in job {job_data['job']['id']}"])
        run_git_command(["push", "origin", "main"])
        
        print(f"Job {job_data['job']['id']} failed: {e}")
        return False

def main():
    print("Starting Simple Job Poller...")
    print(f"Monitoring: {JOB_FILE}")
    
    # Create job file if it doesn't exist
    if not JOB_FILE.exists():
        initial_data = {
            "status": "idle",
            "job": {
                "id": None,
                "command": None
            },
            "result": {
                "stdout": None,
                "stderr": None,
                "return_code": None
            }
        }
        with open(JOB_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        run_git_command(["add", "remote_job.json"])
        run_git_command(["commit", "-m", "Initialize remote job file"])
        run_git_command(["push", "origin", "main"])
    
    while True:
        try:
            # Check for remote changes
            if check_for_remote_changes():
                print("Remote changes detected, pulling updates...")
                run_git_command(["pull", "origin", "main"])
                
                # Process job if available
                process_job()
            else:
                print(f"No changes. Sleeping for {POLL_INTERVAL} seconds...")
                
        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()