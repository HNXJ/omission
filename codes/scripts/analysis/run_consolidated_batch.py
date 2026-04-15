#!/usr/bin/env python3
"""
Overnight LFP TFR Band Power Batch Processor
Computes TFR band power across all channels, sessions, areas, and conditions.
"""
from __future__ import annotations
import subprocess
from pathlib import Path
import os

# Assuming existing figures script remains in the loop
FIGURES = [3, 4, 5, 6, 7, 8]
PYTHON_EXE = r"C:\Python314\python.exe"

def run_batch():
    print(f"""[action] Starting consolidated overnight batch.""")
    
    # 1. Run Figure Generation (Existing)
    # We call the existing overnight batch script
    figure_batch = Path(r"D:\drive\omission\codes\scripts\analysis\run_overnight_batch.py")
    if figure_batch.exists():
        print(f"""[action] Starting Figure batch...""")
        subprocess.run([PYTHON_EXE, str(figure_batch)], check=True)
    
    # 2. Run LFP TFR Band Power Batch
    tfr_script = Path(r"D:\drive\omission\codes\scripts\analysis\run_omission_local_tfr.py")
    if tfr_script.exists():
        print(f"""[action] Starting LFP TFR Batch...""")
        # We assume the script handles iteration over all sessions/conditions internally
        subprocess.run([PYTHON_EXE, str(tfr_script)], check=True)
    else:
        print(f"""[action] LFP TFR script not found at {tfr_script}""")

    print(f"""[action] Overnight batch complete.""")

if __name__ == "__main__":
    run_batch()
