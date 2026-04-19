# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_divergence_latency(results: dict, output_dir: str):
    """
    Plots Figure 26: State Divergence Latency across Hierarchy.
    """
    # Trace 1: Accuracies over time
    plotter = OmissionPlotter(
        title="Figure 26A: Decoding Divergence over Time",
        subtitle="Standard vs Omission (AXAB) | 0ms = Omission Onset"
    )
    plotter.set_axes("Time from Omission", "ms", "Decoding Accuracy", "fraction")
    
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    areas = list(results.keys())
    
    for i, area in enumerate(areas):
        data = results[area]
        plotter.add_trace(
            go.Scatter(x=data['times'], y=data['accuracy_mean'], mode='lines', line=dict(color=colors[i%len(colors)], width=3), name=area),
            name=area
        )
        
    plotter.add_xline(0, "Omission Onset", color="red")
    plotter.add_yline(0.5, "Chance", color="gray", dash="dot")
    plotter.save(output_dir, "fig26A_accuracy_timeseries")
    
    # Trace 2: Latency Bar Plot
    plotter_bar = OmissionPlotter(
        title="Figure 26B: Omission Latency Hierarchy",
        subtitle="First Time Point > 0.65 Accuracy"
    )
    plotter_bar.set_axes("Area", "Hierarchy", "Latency", "ms")
    
    latencies = [results[area]['latency_mean'] for area in areas]
    stds = [results[area]['latency_std'] for area in areas]
    
    plotter_bar.add_trace(
        go.Bar(x=areas, y=latencies, marker_color="#8F00FF", error_y=dict(type='data', array=stds, visible=True)),
        name="Latency"
    )
    plotter_bar.save(output_dir, "fig26B_latency_hierarchy")
