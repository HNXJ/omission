# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_spike_triggered_average(results: dict, output_dir: str):
    """
    Plots STA across areas.
    """
    plotter = OmissionPlotter(
        title="Figure 32: Spike-Triggered Average (STA)",
        subtitle="Average local LFP waveform triggered on single-unit spikes during Omission window."
    )
    plotter.set_axes("Time from Spike", "ms", "LFP Amplitude", "uV")
    
    for area, data in results.items():
        t = data["t"]
        mean = data["sta_mean"]
        sem = data["sta_sem"]
        
        plotter.add_trace(go.Scatter(
            x=np.concatenate([t, t[::-1]]),
            y=np.concatenate([mean - sem, (mean + sem)[::-1]]),
            fill='toself',
            fillcolor='rgba(200, 200, 200, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        ), name=f"{area}_SEM")
        
        plotter.add_trace(go.Scatter(x=t, y=mean, name=area), name=area)
        
    plotter.add_xline(0, "Spike Time", color="black", dash="dot")
    plotter.save(output_dir, "fig32_spike_triggered_average")
