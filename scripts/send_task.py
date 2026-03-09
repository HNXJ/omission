import os
import json
import uuid
import subprocess
import argparse
from datetime import datetime

BUS_PATH = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini/COMMAND_BUS.json"
REPO_DIR = "/Users/hamednejat/workspace/HNXJ/hnxj-gemini"

def get_hostname():
    import platform
    return "OfficeMac" if platform.system() == "Darwin" else "WindowsPC"

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
    
    # Push to GitHub
    hostname = get_hostname()
    branch = "W" if hostname == "WindowsPC" else "main"
    
    subprocess.run(["git", "-C", REPO_DIR, "add", "COMMAND_BUS.json"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"New task from {hostname}: {task_id}"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "push", "origin", branch], capture_output=True)
    
    print(f"🚀 Task {task_id} sent to {target}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a task to another PC via the GitHub message bus.")
    parser.add_argument("target", choices=["OfficeMac", "WindowsPC", "MainAgent"], help="Target machine")
    parser.add_argument("command", help="The shell command to execute")
    args = parser.parse_args()
    
    send_task(args.target, args.command)
