import os
import json
import time
import subprocess
from datetime import datetime

# Path to the private command bus in the hnxj-gemini repo
BUS_PATH = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini/COMMAND_BUS.json"
REPO_DIR = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini"

def get_hostname():
    # Detect if we are OfficeMac or Windows
    import platform
    return "OfficeMac" if platform.system() == "Darwin" else "WindowsPC"

def poll_commands():
    hostname = get_hostname()
    print(f"📡 {hostname} Task Runner Started. Polling {BUS_PATH}...")
    
    while True:
        try:
            # 1. Sync repo to get latest commands
            subprocess.run(["git", "-C", REPO_DIR, "pull", "origin", "main"], capture_output=True)
            
            if not os.path.exists(BUS_PATH):
                time.sleep(30)
                continue
                
            with open(BUS_PATH, "r") as f:
                bus = json.load(f)
            
            # 2. Check for tasks assigned to this host
            pending_tasks = [t for t in bus.get("tasks", []) if t["target"] == hostname and t["status"] == "pending"]
            
            for task in pending_tasks:
                print(f"🚀 Executing Task [{task['id']}]: {task['command']}")
                task["status"] = "running"
                task["start_time"] = datetime.now().isoformat()
                
                # Update status immediately
                save_bus(bus)
                
                # 3. Execute
                try:
                    result = subprocess.run(task["command"], shell=True, capture_output=True, text=True)
                    task["status"] = "completed"
                    task["output"] = result.stdout + result.stderr
                    task["exit_code"] = result.returncode
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                
                task["end_time"] = datetime.now().isoformat()
                print(f"✅ Task [{task['id']}] finished.")
                
                # 4. Save and Push
                save_bus(bus)
                push_results()
                
        except Exception as e:
            print(f"❌ Error in poll loop: {e}")
            
        time.sleep(30)

def save_bus(bus):
    with open(BUS_PATH, "w") as f:
        json.dump(bus, f, indent=4)

def push_results():
    hostname = get_hostname()
    branch = "W" if hostname == "WindowsPC" else "main"
    
    # Ensure we are on the correct branch before pushing
    subprocess.run(["git", "-C", REPO_DIR, "checkout", branch], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "add", "."], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"Update from {hostname}"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "push", "origin", branch], capture_output=True)

if __name__ == "__main__":
    poll_commands()
