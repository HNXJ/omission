# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_ppc_spectrum(results: dict, output_dir: str):
    """
    Plots PPC Spectrum.
    """
    plotter = OmissionPlotter(
        title="Figure 34: Spike-Field Pairwise Phase Consistency (PPC)",
        subtitle="Bias-free phase-locking strength during Omission window."
    )
    plotter.set_axes("Frequency", "Hz", "PPC Strength", "norm")
    
    for area, data in results.items():
        freqs = data["freqs"]
        mean = data["ppc_mean"]
        sem = data["ppc_sem"]
        
        plotter.add_trace(go.Scatter(x=freqs, y=mean, name=area, mode='lines+markers'), name=area)
        
    plotter.fig.update_xaxes(type="log")
    plotter.save(output_dir, "fig34_spike_phase_consistency")
