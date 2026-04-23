# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_laminar_pac(results: dict, output_dir: str):
    """
    Plots Figure 44: Laminar Phase-Amplitude Coupling.
    """
    mat = results["mi_matrix"]
    layers = results["layers"]
    
    plotter = OmissionPlotter(
        title="Figure 44: Laminar Phase-Amplitude Coupling (PAC)",
        subtitle="Alpha Phase (8-13Hz) -> Gamma Amplitude (30-80Hz) | Tort MI"
    )
    plotter.set_axes("Amplitude Layer", "Depth", "Phase Layer", "Depth")
    
    heatmap = go.Heatmap(
        z=mat, 
        x=layers, 
        y=layers, 
        colorscale="Viridis",
        colorbar=dict(title="Modulation Index (MI)")
    )
    
    plotter.add_trace(heatmap, name="Laminar PAC")
    # Reverse Y axis to have L1 at top
    plotter.fig.update_yaxes(autorange="reversed")
    
    plotter.save(output_dir, "f044_laminar_pac")
