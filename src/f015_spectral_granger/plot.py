# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_global_mi_dynamics(tensor: dict, output_dir: str):
    """
    Plots Figure 15 global MI dynamics over 17 frames.
    """
    bands = ["Theta", "Alpha", "Beta", "Gamma"]
    colors = {"Theta": "#4B0082", "Alpha": "#0000FF", "Beta": "#8F00FF", "Gamma": "#CFB87C"}
    
    # Assuming frames are keys in AXAB
    frame_keys = list(tensor["AXAB"].keys())
    x = np.arange(len(frame_keys))
    
    plotter = OmissionPlotter(title="Figure 15: Global Connectivity Dynamics", subtitle="Mean Inter-Area MI (17 Frames, x_label="Frequency", y_label="Causality (GC)")")
    plotter.set_axes("Frame", "Temporal Context", "Mean MI", "bits")
    
    for cond in ["AAAB", "AXAB"]:
        for b in bands:
            y_mean = [np.mean(tensor[cond][fk][b]) for fk in frame_keys]
            y_sem = [np.std(tensor[cond][fk][b]) / np.sqrt(len(tensor[cond][fk][b])) for fk in frame_keys]
            plotter.add_shaded_error_bar(x, y_mean, y_sem, name=f"{cond}_{b}", color=colors[b])
            print(f"""[action] Added shaded error bar for {cond} {b}""")
            
    plotter.fig.update_xaxes(tickvals=x, ticktext=frame_keys)
    plotter.save(output_dir, "fig15_global_mi_dynamics")
