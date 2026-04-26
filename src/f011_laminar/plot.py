import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np
import os

def plot_laminar_routing(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    for area, pop_hg in results.items():
        plotter = OmissionPlotter(
            title=f"Figure f011: {area} Laminar Cortical Mapping",
            subtitle="High-Gamma (35-80 Hz) Depth-Profile Aligned to Layer 4 Sink"
        )
        # Ensure pure white background, black axis
        plotter.fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#000000", family="Arial"),
            title=dict(font=dict(color="#000000", size=22))
        )
        
        time_ms = np.linspace(-2000, 2000, pop_hg.shape[1])
        channels = np.arange(pop_hg.shape[0]) - pop_hg.shape[0] // 2 # Relative depth centered at 0
        
        plotter.add_trace(go.Heatmap(
            z=pop_hg,
            x=time_ms,
            y=channels,
            colorscale='Magma', # Heatmap colors
            colorbar=dict(title="HG Power (Z)"),
            zmin=np.nanpercentile(pop_hg, 5),
            zmax=np.nanpercentile(pop_hg, 95)
        ), "High-Gamma Laminar Heatmap")

        plotter.set_axes("Time from Omission", "ms", "Relative Depth to L4", "channels")
        
        filename = f"f011_laminar_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html and SVG.")
