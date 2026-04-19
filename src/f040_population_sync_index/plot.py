# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_population_sync_index(results: dict, output_dir: str):
    """
    Plots PSI (Bar chart).
    """
    plotter = OmissionPlotter(
        title="Figure 40: Population Synchronization Index (PSI)",
        subtitle="Average unit-to-LFP synchronization (Beta-band) per area."
    )
    plotter.set_axes("Area", "Hierarchy", "Sync Index (PSI)", "PLV")
    
    areas = list(results.keys())
    psis = [results[a]["psi"] for a in areas]
    stds = [results[a]["psi_std"] for a in areas]
    
    plotter.add_trace(go.Bar(x=areas, y=psis, error_y=dict(type='data', array=stds), marker_color="#9400D3"), name="PSI")
    plotter.save(output_dir, "fig40_population_sync_index")
