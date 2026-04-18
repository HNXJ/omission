# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.loader import DataLoader

def plot_spectral_harmony(results: dict, areas: list, output_dir: str = "D:/drive/outputs/oglo-8figs/f008"):
    """
    Plots Figure 8 spectral harmony heatmaps.
    """
    for name, mat in results.items():
        band, window = name.split("_")
        plotter = OmissionPlotter(
            title=f"Figure 8: {band} Band Power Correlation",
            subtitle=f"{window} Window (11x11 Cross-Area Harmony)"
        )
        plotter.set_axes("Target Area", "Hierarchy", "Source Area", "Hierarchy")
        
        heatmap = go.Heatmap(
            z=mat, x=areas, y=areas, colorscale="Viridis" if band == "Beta" else "Plasma",
            colorbar=dict(title="Pearson r"), zmin=-0.5, zmax=1.0
        )
        plotter.add_trace(heatmap, name=name)
        plotter.save(output_dir, f"fig8_spectral_harmony_{name}")
