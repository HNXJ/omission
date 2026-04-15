#!/usr/bin/env python3
"""
Overnight Batch Processor for Figures 3-8
Generates area-specific figures with selective unit classification.
"""
from __future__ import annotations
import subprocess
from pathlib import Path
import time

AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
FIGURES = [3, 4, 5, 6, 7, 8]
PYTHON_EXE = r"C:\Python314\python.exe"

def run_batch():
    print(f"""[action] Starting batch regeneration for all areas""")
    for area in AREAS:
        print(f"""[action] Processing Area: {area}""")
        for fig_num in FIGURES:
            script_path = Path(rf"D:\drive\omission\codes\scripts\analysis\generate_figure_{fig_num}.py")
            if script_path.exists():
                print(f"""[action] Executing Figure {fig_num} for {area}""")
                # In a real run, pass area as an argument if scripts support it
                # For now, we assume scripts are refactored to iterate areas
                subprocess.run([PYTHON_EXE, str(script_path)], check=True)
            else:
                print(f"""[action] Script for Figure {fig_num} not found""")
    
    print(f"""[action] Batch regeneration complete.""")

if __name__ == "__main__":
    run_batch()
