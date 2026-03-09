import os
import json
import uuid
import subprocess
import argparse
from datetime import datetime

# --- LOCAL LLM CONFIGURATION (Office Mac M3) ---
# Use this to start: claude --model "local model"
LOCAL_LLM_URL = "https://plugin-primarily-donald-www.trycloudflare.com/v1"
LOCAL_LLM_API_KEY = "sk-lm-F2VX005K:WVPz8lWIzTUD4hVnLzKK"
# -----------------------------------------------

BUS_PATH = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini/COMMAND_BUS.json"
REPO_DIR = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini"

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
        bus = {"last_updated": "", "tasks": []}
    else:
        with open(BUS_PATH, "r") as f:
            bus = json.load(f)
    
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
    
    subprocess.run(["git", "-C", REPO_DIR, "add", "COMMAND_BUS.json"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"New task from {hostname}: {task_id}"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "push", "origin", branch], capture_output=True)
    
    print(f"🚀 Task {task_id} sent from {hostname} (branch {branch}) to {target}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a task to another PC via the GitHub message bus.")
    parser.add_argument("target", choices=["OfficeMac", "WindowsPC", "MainAgent"], help="Target machine")
    parser.add_argument("command", help="The shell command to execute")
    args = parser.parse_args()
    
    send_task(args.target, args.command)
