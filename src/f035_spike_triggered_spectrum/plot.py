# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_spike_triggered_spectrum(results: dict, output_dir: str):
    """
    Plots STS (TFR).
    """
    for area, data in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 35: Spike-Triggered Spectrum - {area}",
            subtitle="TFR of local LFP around spike times."
        )
        plotter.set_axes("Time from Spike", "s", "Frequency", "Hz")
        
        heatmap = go.Heatmap(
            z=10 * np.log10(data["z"]), x=data["t"], y=data["f"], 
            colorscale="Viridis"
        )
        plotter.add_trace(heatmap, name="STS Power")
        plotter.save(output_dir, f"fig35_sts_{area}")
