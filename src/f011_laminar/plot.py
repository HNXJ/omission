import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np
import os

def plot_laminar_routing(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    for area, pop_hg in results.items():
        # Clean data first
        pop_hg = np.nan_to_num(pop_hg, nan=0.0)
        
        # Define axes based on actual data shape
        n_chans, n_times = pop_hg.shape
        time_ms = np.linspace(-2000, 2000, n_times)
        channels = np.arange(n_chans) - n_chans // 2 # Relative depth centered at 0

        plotter = OmissionPlotter(
            title=f"Figure f011: {area} Laminar Cortical Mapping",
            x_label="Time from Omission",
            y_label="Relative Depth to L4",
            subtitle="High-Gamma (35-80 Hz) Depth-Profile Aligned to Layer 4 Sink",
            x_unit="ms",
            y_unit="channels"
        )
        
        # Determine safe color bounds
        if np.any(np.isfinite(pop_hg)):
            zmin = np.nanpercentile(pop_hg, 5)
            zmax = np.nanpercentile(pop_hg, 95)
        else:
            zmin, zmax = 0, 1
            
        plotter.add_trace(go.Heatmap(
            z=pop_hg,
            x=time_ms,
            y=channels,
            colorscale='Magma',
            colorbar=dict(title="HG Power (Z)"),
            zmin=zmin,
            zmax=zmax
        ), "High-Gamma Laminar Heatmap")
        
        filename = f"f011_laminar_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html and SVG.")
