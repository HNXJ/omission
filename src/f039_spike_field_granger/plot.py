# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_spike_field_granger(results: dict, output_dir: str):
    """
    Plots SPK-LFP Cross-Correlation.
    """
    plotter = OmissionPlotter(
        title="Figure 39: Spike-Field Directed Influence",
        subtitle="Lagged Cross-Correlation (SPK vs LFP Envelope)."
    )
    plotter.set_axes("Lag", "ms", "Correlation", "rho")
    
    for area, data in results.items():
        lags = data["lags"]
        mean = data["xcorr_mean"]
        
        # Crop to [-200, 200] ms
        mask = (lags >= -200) & (lags <= 200)
        plotter.add_trace(go.Scatter(x=lags[mask], y=mean[mask], name=area), name=area)
        
    plotter.add_xline(0, "Synchrony", color="black", dash="dot")
    plotter.save(output_dir, "fig39_spike_field_granger")
