# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_global_mi_dynamics(tensor: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f015"):
    """
    Plots Figure 15 global MI dynamics over 17 frames.
    """
    bands = ["Theta", "Alpha", "Beta", "Gamma"]
    colors = {"Theta": "#4B0082", "Alpha": "#0000FF", "Beta": "#8F00FF", "Gamma": "#CFB87C"}
    
    # Assuming frames are keys in AXAB
    frame_keys = list(tensor["AXAB"].keys())
    x = np.arange(len(frame_keys))
    
    plotter = OmissionPlotter(title="Figure 15: Global Connectivity Dynamics", subtitle="Mean Inter-Area MI (17 Frames)")
    plotter.set_axes("Frame", "Temporal Context", "Mean MI", "bits")
    
    for cond in ["AAAB", "AXAB"]:
        dash = "solid" if cond == "AXAB" else "dash"
        for b in bands:
            y = [np.mean(tensor[cond][fk][b]) for fk in frame_keys]
            plotter.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=colors[b], dash=dash), name=f"{cond}_{b}"))
            
    plotter.fig.update_xaxes(tickvals=x, ticktext=frame_keys)
    plotter.save(output_dir, "fig15_global_mi_dynamics")
