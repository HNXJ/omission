# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_laminar_coherence(results: dict, output_dir: str):
    """
    Plots Figure 45: Laminar Coherence (iCOH).
    """
    mat = results["icoh_matrix"]
    layers = results["layers"]
    
    plotter = OmissionPlotter(
        title="Figure 45: Laminar Spectral Coherence (iCOH)",
        subtitle="Beta Band (13-30Hz) | Imaginary Coherence (Bias-Corrected)"
    )
    plotter.set_axes("Target Layer", "Depth", "Source Layer", "Depth")
    
    heatmap = go.Heatmap(
        z=mat, 
        x=layers, 
        y=layers, 
        colorscale="Viridis",
        colorbar=dict(title="iCOH Magnitude")
    )
    
    plotter.add_trace(heatmap, name="Laminar Coherence")
    plotter.fig.update_yaxes(autorange="reversed")
    
    plotter.save(output_dir, "f045_laminar_coherence")
