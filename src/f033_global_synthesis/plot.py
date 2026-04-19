# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_global_synthesis(results: dict, areas: list, output_dir: str):
    """
    Plots Figure 33: Global Hierarchy Synthesis.
    """
    # 1. Radar / Spider Plot of hierarchical properties
    plotter = OmissionPlotter(
        title="Figure 33: Global Omission Synthesis",
        subtitle="Hierarchical Gradients across V1-PFC axis"
    )
    
    metrics = ['surprise_magnitude', 'beta_locking', 'quenching_depth', 'omission_latency']
    # Normalize for radar plot
    norm_results = {area: [] for area in areas}
    for m in metrics:
        vals = [results[area][m] for area in areas]
        v_min, v_max = min(vals), max(vals)
        for i, area in enumerate(areas):
            norm_results[area].append((vals[i] - v_min) / (v_max - v_min + 1e-10))
            
    for area in areas:
        plotter.add_trace(go.Scatterpolar(
            r=norm_results[area],
            theta=metrics,
            fill='toself',
            name=area
        ), name=area)
        
    plotter.fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    plotter.save(output_dir, "fig33_hierarchy_synthesis")
