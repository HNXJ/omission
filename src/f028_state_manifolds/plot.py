# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_manifold_coupling(mat: np.ndarray, areas: list, output_dir: str):
    """
    Plots Figure 28: Pairwise Manifold Coupling (CCA Correlation).
    """
    plotter = OmissionPlotter(
        title="Figure 28: Pairwise Manifold Coupling",
        subtitle="CCA Canonical Correlation | Omission Window | Population PC-Space Alignment"
    )
    plotter.set_axes("Target Area", "Hierarchy", "Source Area", "Hierarchy")
    
    heatmap = go.Heatmap(
        z=mat, x=areas, y=areas, colorscale="Viridis",
        colorbar=dict(title="CCA Correlation")
    )
    plotter.add_trace(heatmap, name="Manifold Coupling")
    plotter.save(output_dir, "fig28_manifold_coupling")
