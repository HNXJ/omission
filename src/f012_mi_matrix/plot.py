# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.loader import DataLoader

def plot_mi_matrix(tensor: dict, areas: list, output_dir: str):
    """
    Plots the Figure 12 MI connectivity matrix.
    """
    # Plot Beta Matrix for Omission Window (p2)
    # Check if key exists (depends on AXAB analysis)
    if "AXAB" in tensor and "p2" in tensor["AXAB"] and "Beta" in tensor["AXAB"]["p2"]:
        mat_beta = tensor["AXAB"]["p2"]["Beta"]
        plotter = OmissionPlotter(
            title="Figure 12: Unit-Area to LFP-Area Beta MI",
            subtitle="Omission Window (p2) | Optimized Engine"
        )
        plotter.set_axes("LFP Area", "Hierarchy", "Unit Area", "Hierarchy")
        
        heatmap = go.Heatmap(
            z=mat_beta, x=areas, y=areas, colorscale="Purples",
            colorbar=dict(title="MI (bits)")
        )
        plotter.add_trace(heatmap, name="Beta MI")
        plotter.save(output_dir, "fig12_beta_mi_matrix_p2")
