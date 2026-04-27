# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_spike_field_coherence(results: dict, output_dir: str):
    """
    Plots SFC Spectrum.
    """
    plotter = OmissionPlotter(
        title="Figure 33: Spike-Field Coherence (SFC)",
        x_label="Frequency",
        y_label="Coherence",
        subtitle="Spectral coherence between single-unit spikes and local LFP.",
        x_unit="Hz",
        y_unit="norm"
    )
    
    for area, data in results.items():
        f = data["freqs"]
        mean = data["coh_mean"]
        sem = data["coh_sem"]
        
        plotter.add_trace(go.Scatter(x=f, y=mean, name=area), name=area)
        
    plotter.fig.update_xaxes(type="log", range=[np.log10(4), np.log10(100)])
    plotter.save(output_dir, "fig33_spike_field_coherence")
