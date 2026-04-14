#!/usr/bin/env python3
"""
Automated NWB Validation Pipeline (Batch Mode).
Uses nwbinspector to ensure data compliance.
"""
import subprocess
import sys
from pathlib import Path

def run_validation():
    nwb_dir = Path(r"D:\analysis\nwb")
    report_dir = Path(r"D:\drive\omission\operations\qc\reports\nwbinspector")
    report_file = report_dir / "batch_report.txt"
    
    # Collect files
    nwb_files = list(nwb_dir.glob("*.nwb"))
    if not nwb_files:
        print("No NWB files found for validation.")
        return

    print(f"Validating {len(nwb_files)} files...")
    
    # Run nwbinspector
    cmd = [
        "nwbinspector", str(nwb_dir),
        "--report-file-path", str(report_file),
        "-o",
        "--n-jobs", "-1"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Validation report saved to: {report_file}")
    except subprocess.CalledProcessError as e:
        print(f"Validation failed with error: {e}")

if __name__ == "__main__":
    run_validation()
