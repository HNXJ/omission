#!/usr/bin/env python3
"""
run_gamma_lfp_comparison_suite.py
Generates grand-average comparison figures for AAAB, AXAB, AAXB, and AAAX.
Overlays frequency bands (Theta, Alpha, Beta, Gamma) in a 2x2 condition grid per area.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fix ModuleNotFoundError
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from codes.functions.lfp.lfp_constants import BANDS, SEQUENCE_TIMING, GOLD, VIOLET, TEAL, ORANGE, BLACK, GRAY
from codes.functions.visualization.lfp_plotting import create_band_plot

ROOT = Path("D:/Analysis/Omission/local-workspace")
CKP_DIR = ROOT / "data/other/checkpoints/lfp_oglo3"
OUT_DIR = ROOT / "figures/oglo3/comparisons"
os.makedirs(OUT_DIR, exist_ok=True)

SESSIONS = ["230629", "230630", "230714", "230719", "230720", "230721", 
            "230816", "230818", "230823", "230825", "230830", "230831", "230901"]
TARGET_CONDS = ["AAAB", "AXAB", "AAXB", "AAAX"]
BAND_COLORS = {
    "Theta": "#008080", # Teal
    "Alpha": "#CFB87C", # Gold
    "Beta": "#8F00FF",  # Violet
    "Gamma": "#FF5E00"  # Orange
}

def run_comparison_suite():
    print("Starting LFP Comparison Suite (AAAB vs AXAB vs AAXB vs AAAX)...")
    
    # Identify unique Area labels from checkpoints
    all_files = list(CKP_DIR.glob("*.npy"))
    areas = sorted(list(set(["_".join(f.stem.split("_")[1:-2]) for f in all_files])))
    
    for area in areas:
        print(f"  Processing Area: {area}")
        
        # Create a 2x2 subplot figure for the 4 conditions
        fig = make_subplots(
            rows=2, cols=2, 
            subplot_titles=TARGET_CONDS,
            shared_xaxes=True, shared_yaxes=True,
            vertical_spacing=0.1, horizontal_spacing=0.05
        )
        
        found_any = False
        
        for i, cond in enumerate(TARGET_CONDS):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            # Add Sequence Patches to each subplot (Step 2)
            for name, info in SEQUENCE_TIMING.items():
                fig.add_vrect(
                    x0=info["start"], x1=info["end"], 
                    fillcolor=info["color"], opacity=0.08, line_width=0,
                    row=row, col=col
                )
            
            for band_name, color in BAND_COLORS.items():
                means = []
                times = None
                
                # Aggregate across sessions
                for sid in SESSIONS:
                    fpath = CKP_DIR / f"ses{sid}_{area}_{cond}_{band_name}.npy"
                    if fpath.exists():
                        data = np.load(fpath, allow_pickle=True).item()
                        means.append(data["mean"])
                        times = data["times"]
                
                if len(means) < 1: continue
                found_any = True
                
                means = np.array(means)
                grand_mean = np.mean(means, axis=0)
                grand_sem = np.std(means, axis=0) / np.sqrt(means.shape[0])
                
                # Add SEM shading
                fig.add_trace(go.Scatter(
                    x=times, y=grand_mean + 2*grand_sem, mode='lines', 
                    line=dict(width=0), showlegend=False,
                    legendgroup=band_name
                ), row=row, col=col)
                
                fig.add_trace(go.Scatter(
                    x=times, y=grand_mean - 2*grand_sem, fill='tonexty', mode='lines', 
                    line=dict(width=0), fillcolor=color, opacity=0.2, 
                    showlegend=False, legendgroup=band_name
                ), row=row, col=col)
                
                # Add Mean Line
                fig.add_trace(go.Scatter(
                    x=times, y=grand_mean, mode='lines', 
                    line=dict(color=color, width=2), 
                    name=band_name if i == 0 else None, # Show in legend only once
                    showlegend=True if i == 0 else False,
                    legendgroup=band_name
                ), row=row, col=col)
        
        if not found_any: continue
        
        fig.update_layout(
            template="plotly_white",
            title=f"Grand Average Spectral Comparison: {area} (n_sessions per cond)",
            xaxis_title="Time (ms)", yaxis_title="Power (dB relative to fx)",
            height=800, width=1000
        )
        # Update all x-axes
        fig.update_xaxes(title_text="Time (ms)", row=2, col=1)
        fig.update_xaxes(title_text="Time (ms)", row=2, col=2)
        # Update all y-axes
        fig.update_yaxes(title_text="Power (dB)", row=1, col=1)
        fig.update_yaxes(title_text="Power (dB)", row=2, col=1)

        fig.write_html(OUT_DIR / f"{area}_comparison_4cond.html")
        fig.write_image(OUT_DIR / f"{area}_comparison_4cond.png")

    print("Comparison Suite Complete.")

if __name__ == "__main__":
    run_comparison_suite()
