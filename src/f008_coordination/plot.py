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
        if name in ["stats", "stars"]: continue
        
        print(f"[action] Plotting Spectral Harmony: {name}")
        band, window = name.split("_")
        
        # Extract stars if available for this band
        text_stars = None
        if "stars" in results and band in results["stars"]:
            text_stars = results["stars"][band]

        plotter = OmissionPlotter(
            title=f"Figure f008: {band} Band Harmony ({window})",
            x_label="Target Area",
            y_label="Source Area",
            subtitle=f"{window} Window (11x11 Cross-Area Harmony)",
            x_unit="Hierarchy",
            y_unit="Hierarchy"
        )
        
        heatmap = go.Heatmap(
            z=mat, x=areas, y=areas, 
            text=text_stars,
            texttemplate="%{text}",
            colorscale="Viridis" if band == "Beta" else "Plasma",
            colorbar=dict(title="Pearson r"), zmin=-0.1, zmax=1.0
        )
        plotter.add_trace(heatmap, name=name)
        
        # Ensure aspect ratio is square for matrices
        plotter.fig.update_layout(width=700, height=700, yaxis=dict(autorange="reversed"))
        
        filename = f"f008_spectral_harmony_{name}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html")
