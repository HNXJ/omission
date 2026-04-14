#!/usr/bin/env python3
"""
Canonical Spiking Dynamics Suite
Integrates unit classification and predictive omission-response analysis.
"""
from pathlib import Path
from codes.functions.spiking.unit_classification import audit_session_units

def run_suite(nwb_path):
    print(f"Running spiking suite for {nwb_path.name}...")
    # 1. Audit and classify units
    audit_res = audit_session_units(nwb_path)
    print(f"Classification: {audit_res}")
    # 2. Run contrast suite...

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nwb", type=Path, required=True)
    args = p.parse_args()
    run_suite(args.nwb)
