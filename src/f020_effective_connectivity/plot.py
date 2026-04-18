# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_effective_connectivity(results: dict):
    """
    Plots Figure 20: Effective Connectivity (Granger Causality).
    results: { 'A->B': [values], ... }
    """
    plotter = OmissionPlotter(
        title="Figure 20: Effective Connectivity (Granger Causality)",
        subtitle="Directed Influence between Areas during Omission"
    )
    plotter.set_axes("Connection Path", "Index", "Granger Causality", "units")
    
    paths = list(results.keys())
    means = [np.mean(results[p]) if results[p] else 0 for p in paths]
    stds = [np.std(results[p]) if results[p] else 0 for p in paths]
    
    # Madelane Golden Dark inspired color palette
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    
    plotter.add_trace(
        go.Bar(
            x=paths, 
            y=means,
            error_y=dict(type='data', array=stds, visible=True),
            marker_color=colors[:len(paths)]
        ),
        name="GC Strength"
    )
            
    output_dir = "D:/drive/outputs/oglo-8figs"
    plotter.save(output_dir, "fig20_effective_connectivity")
