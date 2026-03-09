import os
import json
import time
import subprocess
from datetime import datetime

# --- LOCAL LLM CONFIGURATION (Office Mac M3) ---
# Use this to start: claude --model "local model"
LOCAL_LLM_URL = "https://plugin-primarily-donald-www.trycloudflare.com/v1"
LOCAL_LLM_API_KEY = "sk-lm-F2VX005K:WVPz8lWIzTUD4hVnLzKK"
# -----------------------------------------------

# Path to the private command bus in the hnxj-gemini repo
BUS_PATH = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini/COMMAND_BUS.json"
REPO_DIR = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini"

def get_hostname():
    # Detect if we are OfficeMac or Windows
    import platform
    if platform.system() == "Darwin":
        return "OfficeMac"
    elif platform.system() == "Windows":
        return "WindowsPC"
    else:
        return "MainAgent"

def get_branch():
    hostname = get_hostname()
    if hostname == "OfficeMac": return "M"
    if hostname == "WindowsPC": return "W"
    return "main"

def poll_commands():
    hostname = get_hostname()
    branch = get_branch()
    print(f"📡 {hostname} Task Runner Started on branch '{branch}'. Polling {BUS_PATH}...")
    
    # Export LLM keys for any subprocesses
    os.environ["CLAUDE_BASE_URL"] = LOCAL_LLM_URL
    os.environ["CLAUDE_API_KEY"] = LOCAL_LLM_API_KEY
    
    while True:
        try:
            # 1. Sync repo to get latest commands from all branches
            subprocess.run(["git", "-C", REPO_DIR, "fetch", "origin"], capture_output=True)
            # We always pull from main to get instructions, but push to our own branch
            subprocess.run(["git", "-C", REPO_DIR, "merge", "origin/main"], capture_output=True)
            
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
                push_results()
                
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
    branch = get_branch()
    
    subprocess.run(["git", "-C", REPO_DIR, "checkout", branch], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "add", "."], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"Update from {hostname}"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "push", "origin", branch], capture_output=True)

if __name__ == "__main__":
    poll_commands()
