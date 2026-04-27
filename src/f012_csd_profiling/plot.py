import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np
import os

def plot_mi_matrix(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # Custom Madelane Divergent Colormap
    madelane_divergent = [
        [0.0, "#CFB87C"],  # Sinks (Negative)
        [0.5, "#FFFFFF"],  # Zero (White)
        [1.0, "#9400D3"]   # Sources (Positive)
    ]
    
    for area, data in results.items():
        pop_csd = data["heatmap"]
        stats = data["stats"]
        stars = stats["stars"]
        
        plotter = OmissionPlotter(
            title=f"Figure f012: {area} CSD Profiling {stars}",
            x_label="Time from Omission",
            y_label="Relative Depth to L4",
            subtitle=f"Sink Magnitude: {stats['tier']} (p={stats['p']:.2e}) {stars}",
            x_unit="ms",
            y_unit="channels"
        )
        
        time_ms = np.linspace(-2000, 2000, pop_csd.shape[1])
        channels = np.arange(pop_csd.shape[0]) - pop_csd.shape[0] // 2 # Relative depth centered at 0
        
        # Determine symmetric color limit
        zmax = np.nanpercentile(np.abs(pop_csd), 95) if np.any(pop_csd) else 1.0
        zmin = -zmax
        
        plotter.add_trace(go.Heatmap(
            z=pop_csd,
            x=time_ms,
            y=channels,
            colorscale=madelane_divergent,
            colorbar=dict(title="CSD"),
            zmin=zmin,
            zmax=zmax
        ), "CSD Heatmap")
        
        filename = f"f012_csd_profiling_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html and SVG.")
        
    log.progress("Finished plotting f012 CSD Profiling.")
