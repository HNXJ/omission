#!/usr/bin/env python3
"""
Putative Classification Plotter
Aggregates waveform metrics and plots E/I distribution histograms.
"""
from __future__ import annotations
import pandas as pd
import plotly.express as px
from pathlib import Path

def plot_distributions(metrics_dir: Path, output_dir: Path):
    # Aggregate all CSVs
    files = list(metrics_dir.glob("metrics_*.csv"))
    if not files:
        print("No metric files found.")
        return
    
    df_list = [pd.read_csv(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    
    # Generate E/I distribution plot
    fig = px.histogram(df, x="duration", color="ei_type", nbins=50, 
                       title="Putative E/I Distribution (Waveform Duration)",
                       labels={"duration": "Waveform Duration (ms)", "ei_type": "Classification"})
    
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_dir / "putative_ei_distribution.html")
    print(f"[Saved] Distribution plot to {output_dir}/putative_ei_distribution.html")

if __name__ == "__main__":
    metrics_dir = Path(r"D:\drive\omission\outputs\putative_typing")
    output_dir = Path(r"D:\drive\omission\outputs\oglo-figures\putative")
    plot_distributions(metrics_dir, output_dir)
