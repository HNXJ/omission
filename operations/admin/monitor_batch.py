#!/usr/bin/env python3
"""
Overnight Monitor for Omission Pipeline
Periodically checks the status of background batch processes.
"""
import psutil
import time
from pathlib import Path

# Monitor the specific PID of the consolidated batch
TARGET_PID = 3084 

def monitor():
    try:
        proc = psutil.Process(TARGET_PID)
        if proc.is_running():
            print(f"""[monitor] Batch process {TARGET_PID} is still running.""")
        else:
            print(f"""[monitor] Batch process {TARGET_PID} finished with exit code {proc.returncode()}.""")
    except psutil.NoSuchProcess:
        print(f"""[monitor] Batch process {TARGET_PID} not found. Assuming finished or failed.""")

if __name__ == "__main__":
    while True:
        monitor()
        time.sleep(3600)  # Check every hour
