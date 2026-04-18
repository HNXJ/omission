# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_connectivity_delta(tensor: dict, areas: list, output_dir: str = "D:/drive/outputs/oglo-8figs/f014"):
    """
    Plots Figure 14 connectivity delta (AXAB - AAAB) heatmaps.
    """
    if "AXAB" not in tensor or "AAAB" not in tensor: return
    
    # Delta MI: Omission Window (p2)
    delta_beta = tensor["AXAB"]["p2"]["Beta"] - tensor["AAAB"]["p2"]["Beta"]
    delta_gamma = tensor["AXAB"]["p2"]["Gamma"] - tensor["AAAB"]["p2"]["Gamma"]
    
    # Beta
    plotter = OmissionPlotter(title="Figure 14: Beta Connectivity Delta", subtitle="Omission Window (p2)")
    plotter.set_axes("LFP Area", "Hierarchy", "Unit Area", "Hierarchy")
    plotter.add_trace(go.Heatmap(z=delta_beta, x=areas, y=areas, colorscale="RdBu", zmid=0, colorbar=dict(title="ΔMI")), name="ΔBeta MI")
    plotter.save(output_dir, "fig14_delta_mi_beta_p2")
    
    # Gamma
    plotter_g = OmissionPlotter(title="Figure 14: Gamma Connectivity Delta", subtitle="Omission Window (p2)")
    plotter_g.set_axes("LFP Area", "Hierarchy", "Unit Area", "Hierarchy")
    plotter_g.add_trace(go.Heatmap(z=delta_gamma, x=areas, y=areas, colorscale="RdBu", zmid=0, colorbar=dict(title="ΔMI")), name="ΔGamma MI")
    plotter_g.save(output_dir, "fig14_delta_mi_gamma_p2")
