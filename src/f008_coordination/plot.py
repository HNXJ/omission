import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import os

def plot_spectral_harmony(results: dict, areas: list, output_dir: str):
    """
    Plots Figure f008 spectral harmony heatmaps.
    """
    os.makedirs(output_dir, exist_ok=True)
    for name, mat in results.items():
        print(f"[action] Plotting Spectral Harmony: {name}")
        band, window = name.split("_")
        plotter = OmissionPlotter(
            title=f"Figure f008: {band} Band Power Correlation",
            subtitle=f"{window} Window (11x11 Cross-Area Harmony)"
        )
        plotter.set_axes("Target Area", "Hierarchy", "Source Area", "Hierarchy")
        
        heatmap = go.Heatmap(
            z=mat, x=areas, y=areas, 
            colorscale="Viridis" if band == "Beta" else "Plasma",
            colorbar=dict(title="Pearson r"), zmin=-0.1, zmax=1.0
        )
        plotter.add_trace(heatmap, name=name)
        
        # Ensure aspect ratio is square for matrices
        plotter.fig.update_layout(width=700, height=700, yaxis=dict(autorange="reversed"))
        
        filename = f"f008_spectral_harmony_{name}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html")
