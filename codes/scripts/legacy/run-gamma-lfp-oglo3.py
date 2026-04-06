#!/usr/bin/env python3
"""
run_gamma_lfp_oglo3.py
Master execution of the 15-Step GAMMA PLAN for LFP-only omission analysis.
Generates the "OMISSION 2026 Systematic Figure Suite" in oglo3/.
"""

from codes.config.paths import PROJECT_ROOT

import sys
import os
from pathlib import Path

# Fix ModuleNotFoundError
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- Import Functional Core ---
from codes.functions.lfp.lfp_constants import GOLD, BLACK, VIOLET, PINK, TIMING_MS, BANDS, HIERARCHY
from codes.functions.lfp.lfp_tfr import compute_multitaper_tfr, get_band_power
from codes.functions.visualization.lfp_plotting import create_tfr_figure, create_band_plot
from codes.functions.lfp.lfp_connectivity import compute_pairwise_coherence

# --- Setup Paths ---
ROOT = Path(PROJECT_ROOT)
DATA_DIR = ROOT / "data/arrays"
MAP_FILE = ROOT / "data/other/checkpoints/vflip2_mapping_v3.csv"
OUT_DIR = ROOT / "figures/oglo3"
CKP_DIR = ROOT / "data/other/checkpoints/lfp_oglo3"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(CKP_DIR, exist_ok=True)

# --- Load Mapping ---
MAPPING_DF = pd.read_csv(MAP_FILE)

def get_area(sid, pid):
    """Retrieves area label from mapping."""
    # Handle both string and int sid
    row = MAPPING_DF[(MAPPING_DF['session_id'].astype(str) == str(sid)) & 
                     (MAPPING_DF['probe_id'] == pid)]
    if not row.empty:
        return row['area'].values[0]
    return "Unknown"

# --- Manifest ---
SESSIONS = ["230629", "230630", "230714", "230719", "230720", "230721", 
            "230816", "230818", "230823", "230825", "230830", "230831", "230901"]
CONDS = ["AAAB", "AAAX", "AAXB", "AXAB", "BBBA", "BBBX", "BBXA", "BXBA", "RRRR", "RRRX", "RRXR", "RXRR"]
PROBES = [0, 1, 2] # Up to 3 probes per session

def run_gamma_oglo3():
    print("Starting GAMMA MASTER PIEPLINE (V4 Suite)...")
    
    # --- Loop Sessions ---
    for sid in SESSIONS:
        print(f"  Processing Session: {sid}")
        # Create session output folder
        ses_out = OUT_DIR / f"ses{sid}"
        os.makedirs(ses_out, exist_ok=True)
        
        # --- Loop Conditions ---
        for cond in CONDS:
            for pid in PROBES:
                area = get_area(sid, pid)
                area_clean = area.replace("/", "_").replace("\\", "_").replace(", ", "_")
                fname = DATA_DIR / f"ses{sid}-probe{pid}-lfp-{cond}.npy"
                if not fname.exists(): continue
                
                # Load LFP (trials, ch, time)
                lfp = np.load(fname, mmap_mode='r')
                lfp = np.nan_to_num(lfp) # Mandatory Sanitation
                
                # Pick a representative channel (e.g., channel 32 - Step 1)
                sig = lfp[:, 32, :] 
                
                # --- Step 6: TFR ---
                # Align such that p1 (Sample 1000) is 0ms.
                # Use window -500ms to 4500ms (to catch d4)
                sig_aligned = sig[:, 500:6000] # -500ms to 5000ms
                f, t, pwr_trials = compute_multitaper_tfr(sig_aligned) # Need trial-wise for SEM
                
                # Normalize and average
                # baseline (fx) is -1000 to 0. In aligned, it's 0 to 0.5s.
                base_idx = (t >= 0.0) & (t <= 0.5)
                base_pwr = np.mean(pwr_trials[:, :, base_idx], axis=(0, 2), keepdims=True) # trials x freqs x time
                
                pwr_db_trials = 10 * np.log10(pwr_trials / (base_pwr + 1e-12))
                pwr_db_mean = np.mean(pwr_db_trials, axis=0) # (freqs x time)
                
                # --- Fig 05: Per-Condition TFR ---
                fig_tfr = create_tfr_figure(f, (t-0.5)*1000, pwr_db_mean, 
                                           title=f"TFR: {sid} {area} {cond}")
                fig_tfr.write_html(ses_out / f"{cond}_{area_clean}_tfr.html")
                
                # --- Step 7: Band Extraction ---
                times_ms = (t-0.5)*1000
                for band_name, lims in BANDS.items():
                    band_db_trials = get_band_power(f, pwr_db_trials, lims) # trials x time
                    mean_traj = np.mean(band_db_trials, axis=0)
                    sem_traj = np.std(band_db_trials, axis=0) / np.sqrt(band_db_trials.shape[0])
                    
                    # Save for aggregation
                    save_path = CKP_DIR / f"ses{sid}_{area_clean}_{cond}_{band_name}.npy"
                    np.save(save_path, {"mean": mean_traj, "sem": sem_traj, "times": times_ms})
                    
                    # --- Fig 06: Band Summary ---
                    fig_band = create_band_plot(times_ms, mean_traj, sem_traj, 
                                               title=f"{band_name}: {sid} {area} {cond}")
                    fig_band.write_html(ses_out / f"{cond}_{area_clean}_{band_name}.html")

    print("GAMMA MASTER PIEPLINE COMPLETE.")

if __name__ == "__main__":
    run_gamma_oglo3()
