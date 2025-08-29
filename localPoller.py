import os
import json
import subprocess
import time
from pathlib import Path

# Configuration
REPO_DIR = "E:\\RemoteTestingMCP"  # Your repository path
JOB_FILE = Path(REPO_DIR) / "remote_job.json"
POLL_INTERVAL = 30  # seconds

def run_git_command(args, capture_output=True):
    """Run git commands in the repo directory."""
    result = subprocess.run(["git"] + args, cwd=REPO_DIR, 
                         capture_output=capture_output, text=True)
    if result.returncode != 0 and capture_output:
        print(f"Git command failed: {' '.join(args)}")
        print(f"Error: {result.stderr}")
    return result

def check_git_status():
    """Check if there are any uncommitted changes or merge conflicts."""
    status_result = run_git_command(["status", "--porcelain"])
    has_changes = bool(status_result.stdout.strip())
    
    # Check for merge conflicts specifically
    has_conflicts = "UU" in status_result.stdout
    
    return has_changes, has_conflicts

def ensure_clean_state():
    """Ensure we have a clean working tree before proceeding."""
    has_changes, has_conflicts = check_git_status()
    
    if has_conflicts:
        print("Merge conflict detected, aborting merge...")
        run_git_command(["merge", "--abort"])
        # After aborting, check status again
        has_changes, has_conflicts = check_git_status()
    
    if has_changes:
        print("Uncommitted changes detected, committing them...")
        run_git_command(["add", "."])
        run_git_command(["commit", "-m", "Auto-commit local changes before processing"])
    
    return not has_conflicts  # Return True if state is clean

def pull_latest_changes():
    """Pull the latest changes from remote, ensuring clean state first."""
    if not ensure_clean_state():
        print("Could not resolve git state issues, skipping pull...")
        return False
    
    print("Pulling latest changes...")
    pull_result = run_git_command(["pull", "origin", "main"])
    return pull_result.returncode == 0

def push_changes(commit_message):
    """Push changes to remote, ensuring clean state first."""
    if not ensure_clean_state():
        print("Could not resolve git state issues, skipping push...")
        return False
    
    print(f"Pushing changes: {commit_message}")
    run_git_command(["add", "."])
    run_git_command(["commit", "-m", commit_message])
    push_result = run_git_command(["push", "origin", "main"])
    return push_result.returncode == 0

def check_for_remote_changes():
    """Check if there are any changes on the remote repository."""
    # Fetch updates from remote without merging
    run_git_command(["fetch", "origin"])
    
    # Check if our local branch is behind the remote
    result = run_git_command(["rev-list", "--count", "HEAD..origin/main"])
    return result.returncode == 0 and int(result.stdout.strip()) > 0

def ensure_job_file():
    """Ensure the job file exists with proper structure."""
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
        
        push_changes("Initialize remote job file")
        return True
    return False

def read_job_file():
    """Safely read the job file."""
    try:
        with open(JOB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading job file: {e}")
        # Reinitialize the file if it's corrupted
        ensure_job_file()
        return read_job_file()

def write_job_file(data):
    """Safely write to the job file."""
    with open(JOB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def process_job():
    """Process the job if one exists."""
    job_data = read_job_file()
    
    # Check if there's a pending job
    if job_data["status"] != "pending":
        return False
    
    # Update status to processing
    job_data["status"] = "processing"
    write_job_file(job_data)
    
    if not push_changes("Started processing job"):
        return False
    
    try:
        # Execute the command
        command = job_data["job"]["command"]
        print(f"Executing: {command}")
        
        # Execute the command without periodic polling
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Update with results
        job_data["status"] = "completed"
        job_data["result"] = {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode
        }
        
        write_job_file(job_data)
        
        # Push results
        if push_changes(f"Completed job {job_data['job']['id']}"):
            print(f"Job {job_data['job']['id']} completed successfully")
            return True
        else:
            print(f"Failed to push results for job {job_data['job']['id']}")
            return False
        
    except Exception as e:
        # Update with error
        job_data["status"] = "error"
        job_data["result"] = {
            "stdout": "",
            "stderr": str(e),
            "return_code": 1
        }
        
        write_job_file(job_data)
        
        push_changes(f"Error in job {job_data['job']['id']}")
        print(f"Job {job_data['job']['id']} failed: {e}")
        return False

def main():
    print("Starting Enhanced Job Poller...")
    print(f"Monitoring: {JOB_FILE}")
    
    # Ensure job file exists
    ensure_job_file()
    
    last_poll_time = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Only check for remote changes at the specified interval
            if current_time - last_poll_time >= POLL_INTERVAL:
                # Check for remote changes
                if check_for_remote_changes():
                    print("Remote changes detected, updating...")
                    
                    # Pull the latest changes
                    if pull_latest_changes():
                        # Process job if available
                        process_job()
                    else:
                        print("Failed to pull changes, skipping processing...")
                else:
                    print(f"No remote changes detected. Next check in {POLL_INTERVAL} seconds...")
                
                last_poll_time = current_time
            else:
                # Sleep for a short time before checking again
                time.sleep(1)
                
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(POLL_INTERVAL)  # Wait before retrying

if __name__ == "__main__":
    main()