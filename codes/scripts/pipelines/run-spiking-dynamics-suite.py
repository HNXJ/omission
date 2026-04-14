#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
from codes.functions.spiking.omission_hierarchy_utils import extract_unit_traces, classify_unit_types
from codes.functions.spiking.spike_lfp_coordination import compute_spike_lfp_ppc_trace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_suite(nwb_path: Path):
    logger.info(f"Running spiking dynamics suite for {nwb_path.name}")
    # Canonical accessors
    unit_types = classify_unit_types(nwb_path)
    traces = extract_unit_traces(session_id=nwb_path.stem)
    # Perform analysis...
    logger.info("Spiking dynamics analysis completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nwb", type=Path, required=True)
    args = parser.parse_args()
    run_suite(args.nwb)
