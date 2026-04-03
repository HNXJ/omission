"""
lfp_plotting.py
Plotting utilities for LFP Omission figures.
Standardizes Plotly, gold/black/violet palette, and ms-based time axes.
"""
import plotly.graph_objects as go
from codes.functions.lfp_constants import GOLD, BLACK, VIOLET, PINK, TIMING_MS

def create_tfr_figure(freqs, times_ms, power, title="LFP TFR (dB)"):
    """
    Creates standardized TFR Heatmap (Step 6).
    """
    fig = go.Figure(data=go.Heatmap(
        z=power, x=times_ms, y=freqs, colorscale="Viridis"
    ))
    
    # Add Sequence Event Lines
    for name, t_ms in TIMING_MS.items():
        fig.add_vline(x=t_ms, line_dash="dash", line_color=BLACK, 
                      annotation_text=name, annotation_position="top")
        
    # Highlight Omission (Pink Transparent Patch)
    # p4 window is 3093 to 3624 ms
    fig.add_vrect(x0=3093, x1=3624, fillcolor=PINK, opacity=0.2, line_width=0)

    fig.update_layout(
        template="plotly_white", title=title,
        xaxis_title="Time (ms)", yaxis_title="Frequency (Hz)"
    )
    return fig

def create_band_plot(times_ms, mean_pwr, sem_pwr, title="Band Power Trajectory"):
    """
    Creates standardized band trajectory plot (Step 7).
    """
    fig = go.Figure()
    # Add +/- 2SEM shading (Standard)
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr + 2*sem_pwr, mode='lines', line=dict(width=0), 
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr - 2*sem_pwr, fill='tonexty', mode='lines', 
        line=dict(width=0), fillcolor='rgba(207,184,124,0.2)', showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=times_ms, y=mean_pwr, mode='lines', line=dict(color=GOLD), 
        name="Mean Power"
    ))
    
    # Add omission patch (Step 2)
    fig.add_vrect(x0=3093, x1=3624, fillcolor=PINK, opacity=0.15, line_width=0)
    
    fig.update_layout(template="plotly_white", title=title)
    return fig
