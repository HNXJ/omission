#!/usr/bin/env python3

def main(args=None):
    """
    run_gamma_lfp_aggregation.py
    Aggregates LFP spectral results across sessions by condition and area.
    """
    from codes.config.paths import PROJECT_ROOT
    import sys
    import os
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    # Fix ModuleNotFoundError
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from codes.functions.lfp.lfp_constants import BANDS, HIERARCHY
    from codes.functions.visualization.lfp_plotting import create_band_plot
    ROOT = Path(PROJECT_ROOT)
    CKP_DIR = ROOT / "data/other/checkpoints/lfp_oglo3"
    OUT_DIR = ROOT / "figures/oglo3/all_sessions"
    os.makedirs(OUT_DIR, exist_ok=True)
    SESSIONS = ["230629", "230630", "230714", "230719", "230720", "230721", 
            "230816", "230818", "230823", "230825", "230830", "230831", "230901"]
    CONDS = ["AAAB", "AAAX", "AAXB", "AXAB", "BBBA", "BBBX", "BBXA", "BXBA", "RRRR", "RRRX", "RRXR", "RXRR"]
    AREAS = ["V1", "V2", "V4", "MT", "MST", "TEO", "FST", "FEF", "PFC", "Unknown"]
    def run_lfp_aggregation():
    print("Starting LFP Aggregation (All Sessions)...")
    # Identify unique (Area, Cond, Band) combinations from files
    all_files = list(CKP_DIR.glob("*.npy"))
    unique_combinations = set()
    for f in all_files:
        # Expected format: sesSID_AREA_COND_BAND.npy
        parts = f.stem.split("_")
        if len(parts) < 4: continue
        # AREA can have underscores if we're not careful, but sesSID is first.
        # Let's use a more robust split
        # Stem example: ses230629_V1,V2_AAAB_Alpha
        # sid = parts[0]
        # band = parts[-1]
        # cond = parts[-2]
        # area = "_".join(parts[1:-2])
        unique_combinations.add(("_".join(parts[1:-2]), parts[-2], parts[-1]))
    for area, cond, band in sorted(unique_combinations):
        print(f"  Aggregating: {area} {cond} {band}")
        cond_out = OUT_DIR / cond
        os.makedirs(cond_out, exist_ok=True)
        means = []
        times = None
        # Collect session data
        for sid in SESSIONS:
            fpath = CKP_DIR / f"ses{sid}_{area}_{cond}_{band}.npy"
            if fpath.exists():
                data = np.load(fpath, allow_pickle=True).item()
                means.append(data["mean"])
                times = data["times"]
        if len(means) < 2: continue # Only aggregate if we have more than one session
        # Compute Grand Mean and Grand SEM
        means = np.array(means)
        grand_mean = np.mean(means, axis=0)
        grand_sem = np.std(means, axis=0) / np.sqrt(means.shape[0])
        # Generate Grand Figure
        title = f"ALL SESSIONS: {band} {area} {cond} (n={len(means)})"
        fig = create_band_plot(times, grand_mean, grand_sem, title=title)
        fig.write_html(cond_out / f"{area}_{band}_grand.html")
    print("Aggregation Complete.")
    run_lfp_aggregation()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
