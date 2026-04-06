import os
import json
import uuid
import subprocess
import argparse
from datetime import datetime

# --- CONFIGURATION ---
# Use this to start: claude --model "local model"
LOCAL_LLM_URL = "http://10.32.133.50:4474/v1"
LOCAL_LLM_API_KEY = "sk-lm-F2VX005K:WVPz8lWIzTUD4hVnLzKK"

# Dynamic Path Resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
BUS_PATH = os.path.join(REPO_DIR, "COMMAND_BUS.json")

def get_hostname():
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

def send_task(target, command):
    if not os.path.exists(BUS_PATH):
        bus = {"last_updated": "", "tasks": [], "presence": {}}
    else:
        try:
            with open(BUS_PATH, "r") as f:
                bus = json.load(f)
        except Exception:
            bus = {"last_updated": "", "tasks": [], "presence": {}}
    
    task_id = str(uuid.uuid4())[:8]
    new_task = {
        "id": task_id,
        "sender": get_hostname(),
        "target": target,
        "command": command,
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    }
    
    bus["tasks"].append(new_task)
    bus["last_updated"] = datetime.now().isoformat()
    
    with open(BUS_PATH, "w") as f:
        json.dump(bus, f, indent=4)
    
    # Push to GitHub on our specific branch
    hostname = get_hostname()
    branch = get_branch()
    
    print(f"Pushing task {task_id} to GitHub branch '{branch}'...")
    subprocess.run(["git", "-C", REPO_DIR, "add", "COMMAND_BUS.json"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"New task from {hostname}: {task_id}"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "push", "origin", branch], capture_output=True)
    
    print(f"🚀 Task {task_id} sent from {hostname} to {target}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a task to another PC via the GitHub message bus.")
    parser.add_argument("target", choices=["OfficeMac", "WindowsPC", "MainAgent"], help="Target machine")
    parser.add_argument("command", help="The shell command to execute")
    args = parser.parse_args()
    
    send_task(args.target, args.command)
