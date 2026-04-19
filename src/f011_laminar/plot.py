# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_laminar_routing(results: dict, output_dir: str):
    """
    Plots Figure 11 laminar spectral profiles.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(title=f"Figure 11: {area} Laminar Spectral Profile", subtitle="Omission Window (0-500ms Local) | Top=0, Bottom=1")
        plotter.set_axes("Relative Depth", "Normalized", "Evoked Power", "Mag^2")
        
        plotter.add_trace(go.Scatter(x=data['depths'], y=data['beta'], line=dict(color="#9400D3", width=4)), "Beta (13-30 Hz)")
        plotter.add_trace(go.Scatter(x=data['depths'], y=data['gamma'], line=dict(color="#CFB87C", width=4)), "Gamma (35-80 Hz)")
        
        plotter.save(output_dir, f"fig11_laminar_{area}")
