# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_state_decoding(times: np.ndarray, results: dict, output_dir: str):
    """
    Plots Figure 25: State Decoding Accuracy over time.
    """
    plotter = OmissionPlotter(
        title="Figure 25: Condition Decoding (Standard vs Omission)",
        subtitle="Population Decoder (Logistic Regression) | Window: 100ms, Step: 50ms"
    )
    plotter.set_axes("Time from P1 Onset", "ms", "Decoding Accuracy", "fraction")
    
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    times_adj = times - 1000
    
    for i, (area, data) in enumerate(results.items()):
        plotter.add_shaded_error_bar(
            times_adj, 
            data['mean'], 
            data['sem'], 
            area, 
            colors[i % len(colors)]
        )
        
    plotter.add_xline(0, "P1 Onset", color="black")
    plotter.add_xline(1031, "Omission Onset", color="red")
    plotter.add_yline(0.5, "Chance Level", color="gray", dash="dot")

    plotter.save(output_dir, "fig25_state_decoding")
