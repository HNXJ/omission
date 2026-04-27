# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_spike_phase_locking(results: dict, output_dir: str):
    """
    Plots PLV Spectrum across areas.
    """
    plotter = OmissionPlotter(
        title="Figure 31: Spike-Field Phase Locking (PLV) Spectrum",
        x_label="Frequency",
        y_label="PLV Strength",
        subtitle="Phase-locking strength of single units to local LFP during Omission window (p2).",
        x_unit="Hz",
        y_unit="norm"
    )
    
    for area, data in results.items():
        freqs = data["freqs"]
        mean = data["plv_mean"]
        sem = data["plv_sem"]
        
        # Add ribbon for SEM
        plotter.add_trace(go.Scatter(
            x=np.concatenate([freqs, freqs[::-1]]),
            y=np.concatenate([mean - sem, (mean + sem)[::-1]]),
            fill='toself',
            fillcolor='rgba(200, 200, 200, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        ), name=f"{area}_SEM")
        
        plotter.add_trace(go.Scatter(x=freqs, y=mean, name=area, mode='lines+markers'), name=area)
        
    plotter.fig.update_xaxes(type="log")
    plotter.save(output_dir, "fig31_spike_phase_locking")
