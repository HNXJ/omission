"""
lfp_plotting.py
Plotting utilities for LFP Omission figures.
Standardizes Plotly, gold/black/violet palette, and ms-based time axes.
"""
import plotly.graph_objects as go
from codes.functions.lfp_constants import GOLD, BLACK, VIOLET, PINK, TEAL, ORANGE, GRAY, TIMING_MS, SEQUENCE_TIMING

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

    fig.update_layout(
        template="plotly_white", title=title,
        xaxis_title="Time (ms)", yaxis_title="Frequency (Hz)"
    )
    return fig

def create_band_plot(times_ms, mean_pwr, sem_pwr, title="Band Power Trajectory"):
    """
    Creates standardized band trajectory plot (Step 7) with ±SEM shading.
    """
    fig = go.Figure()
    # Add +/- 2SEM shading (Standard)
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr + 2*sem_pwr, mode='lines', line=dict(width=0), 
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr - 2*sem_pwr, fill='tonexty', mode='lines', 
        line=dict(width=0), fillcolor='rgba(207,184,124,0.2)', showlegend=False,
        name="2 SEM"
    ))
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr, mode='lines', line=dict(color=BLACK, width=2), 
        name="Mean Power"
    ))
    
    # Add full sequence patches (Step 2)
    for name, info in SEQUENCE_TIMING.items():
        fig.add_vrect(x0=info["start"], x1=info["end"], 
                      fillcolor=info["color"], opacity=0.1, line_width=0)
    
    fig.update_layout(template="plotly_white", title=title, 
                      xaxis_title="Time (ms)", yaxis_title="Power (dB)")
    return fig
