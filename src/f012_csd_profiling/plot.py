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
    
    for area, pop_csd in results.items():
        plotter = OmissionPlotter(
            title=f"Figure f012: {area} Current Source Density (CSD)",
            subtitle="Spatiotemporal Heatmap Aligned to Layer 4 Sink"
        )
        
        # Ensure pure white background, black axis
        plotter.fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#000000", family="Arial"),
            title=dict(font=dict(color="#000000", size=22))
        )
        
        time_ms = np.linspace(-2000, 2000, pop_csd.shape[1])
        channels = np.arange(pop_csd.shape[0]) - pop_csd.shape[0] // 2 # Relative depth centered at 0
        
        # Determine symmetric color limit
        zmax = np.nanpercentile(np.abs(pop_csd), 95)
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

        plotter.set_axes("Time from Omission", "ms", "Relative Depth to L4", "channels")
        
        filename = f"f012_csd_profiling_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html and SVG.")
        
    # Plot global summary
    if results:
        global_csd = np.nanmean(np.array(list(results.values())), axis=0)
        plotter = OmissionPlotter(
            title="Figure f012: Global Current Source Density (CSD)",
            subtitle="Spatiotemporal Heatmap Aligned to Layer 4 Sink (Averaged Across All Areas)"
        )
        
        plotter.fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#000000", family="Arial"),
            title=dict(font=dict(color="#000000", size=22))
        )
        
        time_ms = np.linspace(-2000, 2000, global_csd.shape[1])
        channels = np.arange(global_csd.shape[0]) - global_csd.shape[0] // 2
        
        zmax = np.nanpercentile(np.abs(global_csd), 95)
        zmin = -zmax
        
        plotter.add_trace(go.Heatmap(
            z=global_csd,
            x=time_ms,
            y=channels,
            colorscale=madelane_divergent,
            colorbar=dict(title="CSD"),
            zmin=zmin,
            zmax=zmax
        ), "Global CSD Heatmap")

        plotter.set_axes("Time from Omission", "ms", "Relative Depth to L4", "channels")
        
        plotter.save(output_dir, "f012_csd_profiling")
        log.progress(f"Saved f012_csd_profiling.html and SVG (Global Summary).")
