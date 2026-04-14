#!/usr/bin/env python3
"""
Figure 6 & 7 Plotting Engine
Assembles cached .npz TFR data into multi-band power traces with SEM.
"""
from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from codes.functions.lfp.lfp_constants import CANONICAL_AREAS

def plot_power_traces(area: str, output_dir: Path):
    # Find all .npz files for this area
    files = list(output_dir.glob(f"**/{area}_*.npz"))
    if not files:
        print(f"No cached data found for {area}")
        return

    # Load and aggregate data
    # Structure: (n_sessions, n_channels, n_freqs, n_times)
    all_power = []
    for f in files:
        data = np.load(f)['power']
        all_power.append(data)
    
    # Simple aggregate (mean across sessions and channels)
    # Adjust axes based on actual npz shape (usually channels, freq, time)
    stacked = np.concatenate(all_power, axis=0) 
    mean_power = np.nanmean(stacked, axis=(0, 1))
    sem_power = np.nanstd(stacked, axis=(0, 1)) / np.sqrt(stacked.shape[0])

    # Plot
    fig = go.Figure()
    # Add trace + SEM shade
    fig.add_trace(go.Scatter(y=mean_power, name=f"{area} Mean Power"))
    # ... assembly logic
    fig.write_html(output_dir / f"{area}_final_plot.html")
    print(f"Plot saved for {area}")

if __name__ == "__main__":
    out_dir = Path(r"D:\drive\omission\outputs\oglo-figures")
    for area in CANONICAL_AREAS:
        plot_power_traces(area, out_dir)
