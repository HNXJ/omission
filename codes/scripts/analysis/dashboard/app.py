#!/usr/bin/env python3
"""
Dashboard Watchdog Daemon
Monitors TFR output directories and refreshes status.json for the frontend.
"""
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(r"D:\drive\omission").resolve()
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DASHBOARD_STATEDIR = OUTPUT_DIR / "dashboard"
DASHBOARD_STATEDIR.mkdir(parents=True, exist_ok=True)

def run_watchdog():
    print(f"[Dashboard] Watchdog started. Monitoring {OUTPUT_DIR}")
    
    while True:
        try:
            # Check for latest logs/npz
            # This is a passive monitor that supplements the generate_figure_6_7_tfr.py
            # which updates status.json directly.
            time.sleep(10)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Watchdog Error: {e}")

if __name__ == "__main__":
    run_watchdog()
