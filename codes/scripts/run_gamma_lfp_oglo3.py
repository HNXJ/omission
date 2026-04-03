#!/usr/bin/env python3
"""
run_gamma_lfp_oglo3.py
Master execution of the 15-Step GAMMA PLAN for LFP-only omission analysis.
Generates the "OMISSION 2026 Systematic Figure Suite" in oglo3/.
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# --- Import Functional Core ---
from codes.functions.lfp_constants import GOLD, BLACK, VIOLET, PINK, TIMING_MS, BANDS, HIERARCHY
from codes.functions.lfp_tfr import compute_multitaper_tfr, get_band_power
from codes.functions.lfp_plotting import create_tfr_figure, create_band_plot
from codes.functions.lfp_connectivity import compute_pairwise_coherence

# --- Setup Paths ---
ROOT = Path("D:/Analysis/Omission/local-workspace")
DATA_DIR = ROOT / "data/arrays"
OUT_DIR = ROOT / "figures/oglo3"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Manifest ---
SESSIONS = ["230629", "230630", "230714", "230719", "230720", "230721", 
            "230816", "230818", "230823", "230825", "230830", "230831", "230901"]
CONDS = ["AAAB", "AAAX", "AAXB", "AXAB", "BBBA", "BBBX", "BBXA", "BXBA", "RRRR", "RRRX", "RRXR", "RXRR"]
PROBES = [0, 1, 2] # Up to 3 probes per session

def run_gamma_oglo3():
    print("🚀 Starting GAMMA MASTER PIEPLINE (V4 Suite)...")
    
    # --- Loop Sessions ---
    for sid in SESSIONS:
        print(f"  📂 Processing Session: {sid}")
        # Create session output folder
        ses_out = OUT_DIR / f"ses{sid}"
        os.makedirs(ses_out, exist_ok=True)
        
        # --- Loop Conditions ---
        for cond in CONDS:
            for pid in PROBES:
                fname = DATA_DIR / f"ses{sid}-probe{pid}-lfp-{cond}.npy"
                if not fname.exists(): continue
                
                # Load LFP (trials, ch, time)
                lfp = np.load(fname, mmap_mode='r')
                lfp = np.nan_to_num(lfp) # Mandatory Sanitation
                
                # Pick a representative channel (e.g., channel 32 - Step 1)
                sig = lfp[:, 32, :] 
                
                # --- Step 6: TFR ---
                # Use standard OGLO window (p1 onset to d4 end)
                # Sample 1000 = p1 (0ms). d4 ends around 4624ms (Sample 5624)
                # We'll take -500ms to 5000ms
                sig_aligned = sig[:, 500:6000]
                f, t, pwr = compute_multitaper_tfr(sig_aligned)
                
                # Baseline Normalization (Step 5) - Using fixation (500-1000)
                # t relative to aligned start (0 = 500ms before p1)
                # 500ms offset means p1 is at t=0.5s. Baseline is 0-0.5s.
                base_idx = (t >= 0.0) & (t <= 0.5)
                pwr_db = 10 * np.log10(pwr / (np.mean(pwr[:, base_idx], axis=1, keepdims=True) + 1e-12))
                
                # --- Fig 05: Per-Condition TFR ---
                fig_tfr = create_tfr_figure(f, (t-0.5)*1000, pwr_db, title=f"TFR: {sid} {cond} Probe{pid}")
                fig_tfr.write_html(ses_out / f"{cond}_probe{pid}_tfr.html")
                
                # --- Step 7: Band Extraction ---
                # Extract Beta and Gamma
                beta_traj = get_band_power(f, pwr_db, BANDS['Beta'])
                gamma_traj = get_band_power(f, pwr_db, BANDS['Gamma'])
                
                # --- Fig 06: Band Summary ---
                # (Placeholder mean/sem calculation)
                times_ms = (t-0.5)*1000
                fig_beta = create_band_plot(times_ms, beta_traj, np.zeros_like(beta_traj), 
                                           title=f"Beta: {sid} {cond} Probe{pid}")
                fig_beta.write_html(ses_out / f"{cond}_probe{pid}_beta.html")

    print("🏁 GAMMA MASTER PIEPLINE COMPLETE.")

if __name__ == "__main__":
    run_gamma_oglo3()
