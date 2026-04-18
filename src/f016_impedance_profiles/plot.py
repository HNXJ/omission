# beta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

def plot_impedance(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f016"):
    """
    Plots Figure 16 impedance profile.
    """
    z_eff = results['z_eff']
    z_mag = np.abs(z_eff)
    z_phase = np.angle(z_eff, deg=True)
    
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=(f"Impedance Mag (Session {results['session']})", "Impedance Phase (deg)"),
        shared_yaxes=True
    )
    
    fig.add_trace(go.Heatmap(z=z_mag, x=results['freqs'], y=results['depths'], colorscale="Viridis", colorbar=dict(x=0.45)), row=1, col=1)
    fig.add_trace(go.Heatmap(z=z_phase, x=results['freqs'], y=results['depths'], colorscale="RdBu", zmid=0, colorbar=dict(x=1.0)), row=1, col=2)
    
    fig.update_layout(template="plotly_white", width=1200, height=600, xaxis_title="Freq (Hz)", yaxis_title="Depth (mm)")
    
    os.makedirs(output_dir, exist_ok=True)
    fig.write_html(os.path.join(output_dir, f"fig16_impedance_ses{results['session']}.html"))
