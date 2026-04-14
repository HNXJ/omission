#!/usr/bin/env python3
"""
Putative Classification Plotter
Aggregates waveform metrics and plots E/I distribution histograms with extreme detail and smoothing.
"""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from scipy.stats import gaussian_kde

def plot_distributions(metrics_dir: Path, output_dir: Path):
    print(f"""[action] Starting aggregation of metric files from {metrics_dir}""")
    files = list(metrics_dir.glob("metrics_*.csv"))
    if not files:
        print(f"""[action] No metric files found. Aborting.""")
        return
    
    print(f"""[action] Loading {len(files)} files""")
    df_list = [pd.read_csv(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    print(f"""[action] Data concatenated. Initial row count: {len(df)}""")
    
    # Filter values below 0.05ms
    print(f"""[action] Filtering out values below 0.05ms""")
    df = df[df['duration'] >= 0.05]
    print(f"""[action] Filtered row count: {len(df)}""")
    
    # Setup precise binning
    bin_width = 0.05
    bins = np.arange(0.05, 1.55, bin_width)
    print(f"""[action] Defined bins with width {bin_width}: {bins}""")
    
    # Plotting
    fig = go.Figure()
    print(f"""[action] Initialized plotly figure""")
    
    for ei_type in df['ei_type'].unique():
        print(f"""[action] Processing distribution for {ei_type}""")
        subset = df[df['ei_type'] == ei_type]['duration']
        
        # Add histogram
        fig.add_trace(go.Histogram(x=subset, name=ei_type, autobinx=False, xbincode=dict(start=0.05, end=1.55, size=bin_width), opacity=0.6))
        print(f"""[action] Added histogram trace for {ei_type}""")
        
        # Add KDE (smoothing)
        print(f"""[action] Computing KDE for {ei_type}""")
        kde = gaussian_kde(subset)
        x_range = np.linspace(0.05, 1.5, 200)
        fig.add_trace(go.Scatter(x=x_range, y=kde(x_range) * len(subset) * bin_width, name=f"{ei_type} (smoothed)", mode='lines'))
        print(f"""[action] Added smoothed KDE line for {ei_type}""")
        
    fig.update_layout(title="Putative E/I Distribution (Waveform Duration)",
                      xaxis=dict(title="Waveform Duration (ms)", range=[0.05, 1.55]),
                      yaxis=dict(title="Count"))
    print(f"""[action] Updated figure layout""")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"""[action] Verified output directory {output_dir}""")
    fig.write_html(output_dir / "putative_ei_distribution.html")
    print(f"""[action] Saved smoothed distribution plot to {output_dir}/putative_ei_distribution.html""")

if __name__ == "__main__":
    print(f"""[action] Script initialized""")
    metrics_dir = Path(r"D:\drive\omission\outputs\putative_typing")
    output_dir = Path(r"D:\drive\omission\outputs\oglo-figures\putative")
    plot_distributions(metrics_dir, output_dir)
    print(f"""[action] Script execution completed""")
