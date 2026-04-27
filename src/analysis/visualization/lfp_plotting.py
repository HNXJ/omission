"""
lfp_plotting.py
Plotting utilities for LFP Omission figures.
Standardizes Plotly, gold/black/violet palette, and sequence rectangle patches.
"""
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.analysis.lfp.lfp_constants import (
    GOLD, BLACK, VIOLET, PINK, TEAL, ORANGE, GRAY, WHITE,
    SEQUENCE_TIMING_MS as SEQUENCE_TIMING, BANDS
)
from src.analysis.visualization.plotting import OmissionPlotter

def create_tfr_figure(freqs, times_ms, power, title="LFP TFR (dB)", area="V1"):
    """
    Creates standardized TFR Heatmap using OmissionPlotter.
    """
    plotter = OmissionPlotter(
        title=title, 
        x_label="Time from Omission", 
        y_label="Frequency", 
        subtitle=f"Area: {area}",
        x_unit="ms",
        y_unit="Hz"
    )
    
    # Madelane-Compliant Heatmap: Enforce Plasma/Viridis with symmetric dB bounds
    heatmap = go.Heatmap(
        z=power, 
        x=times_ms, 
        y=freqs, 
        colorscale="Viridis", 
        zmin=-3, zmax=3,
        colorbar=dict(title="dB")
    )
    plotter.add_trace(heatmap, name="TFR")
    
    plotter.add_xline(0, "Omission", color="white")
    plotter.fig.update_yaxes(range=[4, 100])
    return plotter

def create_band_plot(times_ms, mean_pwr, sem_pwr, title="Band Power Trajectory", color=GOLD, area="V1"):
    """
    Creates standardized band trajectory plot with ±SEM shading using OmissionPlotter.
    """
    plotter = OmissionPlotter(
        title=title, 
        x_label="Time from Omission", 
        y_label="Power", 
        subtitle=f"Area: {area}",
        x_unit="ms",
        y_unit="dB"
    )
    
    plotter.add_shaded_error_bar(
        x=times_ms, 
        mean=mean_pwr, 
        error_upper=sem_pwr, 
        name="Mean Power", 
        color=color
    )
    
    plotter.add_xline(0, "Omission", color="black")
    return plotter


def plot_band_trajectories(bands: Dict[str, np.ndarray], times_ms: np.ndarray = None) -> go.Figure:
    """Overlays multiple band trajectories in one plot."""
    fig = go.Figure()
    for band, y in bands.items():
        x = times_ms if times_ms is not None else np.arange(len(y))
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=band))
    
    # Add patches
    for name, info in SEQUENCE_TIMING.items():
        fig.add_vrect(x0=info["start"], x1=info["end"], 
                      fillcolor=info["color"], opacity=0.08, line_width=0)
                      
    return _style(fig, "Band Power Trajectories Overlay")


def plot_coherence_network(coh: np.ndarray, band_name: str = "beta") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=f"{band_name} network template", x=0.5, y=0.5, showarrow=False)
    return _style(fig, f"Coherence Network: {band_name}")

def make_multi_area_band_figure(grouped, time_ms, out_html, title, area_order):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    # ... logic for plotting multi-area ...
    pass
