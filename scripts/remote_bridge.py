import os
import json
import time
import subprocess
from datetime import datetime

# --- LOCAL LLM CONFIGURATION (Office Mac M3) ---
# Use this to start: claude --model "local model"
LOCAL_LLM_URL = "http://10.32.133.50:4474/v1"
LOCAL_LLM_API_KEY = "sk-lm-F2VX005K:WVPz8lWIzTUD4hVnLzKK"
# -----------------------------------------------

# Portability: Define paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
BUS_PATH = os.path.join(REPO_DIR, "COMMAND_BUS.json")

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
    print(f"📡 {hostname} Chat Active. Polling {BUS_PATH}...")
    
    # Export LLM keys
    os.environ["CLAUDE_BASE_URL"] = LOCAL_LLM_URL
    os.environ["CLAUDE_API_KEY"] = LOCAL_LLM_API_KEY
    
    while True:
        try:
            # 1. Update Heartbeat (Idle status)
            update_presence(hostname, "idle")
            
            # Sync repo
            subprocess.run(["git", "-C", REPO_DIR, "fetch", "origin"], capture_output=True)
            subprocess.run(["git", "-C", REPO_DIR, "merge", "origin/main"], capture_output=True)
            
            if not os.path.exists(BUS_PATH):
                time.sleep(30)
                continue
                
            with open(BUS_PATH, "r") as f:
                bus = json.load(f)
            
            # 2. Check for tasks
            pending_tasks = [t for t in bus.get("tasks", []) if t["target"] == hostname and t["status"] == "pending"]
            
            for task in pending_tasks:
                print(f"💬 {hostname} is typing... (Executing: {task['command']})")
                update_presence(hostname, "busy")
                
                task["status"] = "running"
                task["start_time"] = datetime.now().isoformat()
                save_bus(bus)
                push_results()
                
                # 3. Execute
                try:
                    result = subprocess.run(task["command"], shell=True, capture_output=True, text=True)
                    task["status"] = "completed"
                    task["output"] = result.stdout + result.stderr
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                
                task["end_time"] = datetime.now().isoformat()
                save_bus(bus)
                push_results()
                print(f"✅ {hostname} sent a response.")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            
        time.sleep(30)

def update_presence(hostname, status):
    if not os.path.exists(BUS_PATH): return
    with open(BUS_PATH, "r") as f:
        bus = json.load(f)
    
    if "presence" not in bus: bus["presence"] = {}
    bus["presence"][hostname] = {
        "status": status,
        "last_seen": datetime.now().isoformat()
    }
    save_bus(bus)
    push_results()

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
