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
from codes.functions.lfp.lfp_constants import (
    GOLD, BLACK, VIOLET, PINK, TEAL, ORANGE, GRAY, WHITE,
    SEQUENCE_TIMING, BANDS
)


def _style(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        template="plotly_white",
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=BLACK, family="Arial"),
        margin=dict(l=60, r=30, t=70, b=50),
    )
    return fig


def create_tfr_figure(freqs, times_ms, power, title="LFP TFR (dB)"):
    """
    Creates standardized TFR Heatmap (Step 6) with full sequence patches.
    """
    fig = go.Figure(data=go.Heatmap(
        z=power, x=times_ms, y=freqs, colorscale="Viridis"
    ))
    
    # Add Sequence Event Rectangle Patches (Step 2)
    for name, info in SEQUENCE_TIMING.items():
        fig.add_vrect(x0=info["start"], x1=info["end"], 
                      fillcolor=info["color"], opacity=0.15, line_width=0)
        fig.add_vline(x=info["start"], line_dash="dash", line_color=BLACK, 
                      annotation_text=name, annotation_position="top")

    fig.update_layout(xaxis_title="Time (ms)", yaxis_title="Frequency (Hz)")
    return _style(fig, title)


def plot_tfr_grid(tfr: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]], title: str = "LFP Time-Frequency Grid") -> go.Figure:
    """Multi-panel TFR Grid with sequence patches."""
    n = max(1, len(tfr))
    fig = make_subplots(rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                        subplot_titles=list(tfr.keys()) if tfr else ["No data"])
    if not tfr:
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return _style(fig, title)
        
    for r, (name, (freqs, times, power)) in enumerate(tfr.items(), start=1):
        fig.add_trace(go.Heatmap(z=power, x=times, y=freqs, colorscale="Viridis", showscale=(r == 1)), row=r, col=1)
        # Add Sequence Patches to each subplot
        for ev, info in SEQUENCE_TIMING.items():
            fig.add_vrect(x0=info["start"], x1=info["end"], 
                          fillcolor=info["color"], opacity=0.1, line_width=0, row=r, col=1)
            fig.add_vline(x=info["start"], line_dash="dash", line_color="rgba(0,0,0,0.35)", line_width=1, row=r, col=1)
            
    fig.update_yaxes(title_text="Hz")
    fig.update_xaxes(title_text="Time (ms)")
    return _style(fig, title)


def create_band_plot(times_ms, mean_pwr, sem_pwr, title="Band Power Trajectory", color=GOLD):
    """
    Creates standardized band trajectory plot (Step 7) with ±SEM shading.
    """
    fig = go.Figure()
    # Add +/- 2SEM shading
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr + 2*sem_pwr, mode='lines', line=dict(width=0), 
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr - 2*sem_pwr, fill='tonexty', mode='lines', 
        line=dict(width=0), fillcolor=f'rgba{tuple(list(int(color[i:i+2], 16) for i in (1, 3, 5)) + [0.2])}', 
        showlegend=False, name="2 SEM"
    ))
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr, mode='lines', line=dict(color=color, width=2), 
        name="Mean Power"
    ))
    
    # Add full sequence patches
    for name, info in SEQUENCE_TIMING.items():
        fig.add_vrect(x0=info["start"], x1=info["end"], 
                      fillcolor=info["color"], opacity=0.1, line_width=0)
    
    fig.update_layout(xaxis_title="Time (ms)", yaxis_title="Power (dB)")
    return _style(fig, title)


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
