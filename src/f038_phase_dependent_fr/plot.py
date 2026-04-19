# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_phase_dependent_fr(results: dict, output_dir: str):
    """
    Plots PDFR (circular histogram proxy).
    """
    plotter = OmissionPlotter(
        title="Figure 38: Phase-Dependent Firing Rate (PDFR)",
        subtitle="Firing rate modulation by local Beta (13-30Hz) phase."
    )
    plotter.set_axes("Phase", "rad", "Relative Firing Rate", "norm")
    
    for area, data in results.items():
        plotter.add_trace(go.Scatter(x=data["bins"], y=data["dist_mean"], name=area, mode='lines+markers'), name=area)
        
    plotter.save(output_dir, "fig38_phase_dependent_fr")
