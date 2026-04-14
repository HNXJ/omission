#!/usr/bin/env python3
"""
Batch NWB Validation & Quality Control Suite.
Runs pynwb-validate and NWBInspector across the data directory.
"""
import os
import subprocess
from pathlib import Path
from datetime import datetime

from codes.config.paths import DATA_DIR, REPORTS_DIR

def run_validation():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_base = REPORTS_DIR / f"qc_{timestamp}"
    report_base.mkdir(parents=True, exist_ok=True)
    
    nwb_files = list(DATA_DIR.rglob("*.nwb"))
    print(f">>> Found {len(nwb_files)} NWB files for validation.")
    
    # 1. PyNWB Schema Validation
    pynwb_dir = report_base / "pynwb_validate"
    pynwb_dir.mkdir(exist_ok=True)
    
    for nwb in nwb_files:
        print(f"  [PyNWB] Validating {nwb.name}...")
        report_path = pynwb_dir / f"{nwb.stem}.json"
        try:
            subprocess.run([
                "pynwb-validate", 
                "--json-output-path", str(report_path),
                str(nwb)
            ], check=False)
        except Exception as e:
            print(f"    Error: {e}")

    # 2. NWBInspector Best Practices
    inspector_dir = report_base / "nwbinspector"
    inspector_dir.mkdir(exist_ok=True)
    report_file = inspector_dir / "full_report.txt"
    
    print(f"  [Inspector] Running NWBInspector on {DATA_DIR}...")
    try:
        subprocess.run([
            "nwbinspector", str(DATA_DIR),
            "--n-jobs", "-1",
            "--report-file-path", str(report_file),
            "-o"
        ], check=False)
        print(f"    Report saved to {report_file}")
    except Exception as e:
        print(f"    Error: {e}")

if __name__ == "__main__":
    run_validation()
