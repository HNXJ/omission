# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_directed_flow(mat: np.ndarray, areas: list, output_dir: str):
    """
    Plots Figure 32: Directed Information Flow Matrix.
    """
    plotter = OmissionPlotter(
        title="Figure 32: Directed Information Flow",
        subtitle="Directed Mutual Information (Lag=50ms) | Omission Window (p2)"
    )
    plotter.set_axes("Target Area", "Hierarchy", "Source Area", "Hierarchy")
    
    heatmap = go.Heatmap(
        z=mat, x=areas, y=areas, colorscale="Reds",
        colorbar=dict(title="Directed MI (bits)")
    )
    plotter.add_trace(heatmap, name="Directed Flow")
    plotter.save(output_dir, "fig32_directed_flow")
