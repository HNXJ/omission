# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_onset_latency(results: dict, output_dir: str):
    """
    Plots Figure 40: Onset Latency Analysis.
    """
    # Plot A: PSTH Overlays
    plotter_psth = OmissionPlotter(
        title="Figure 40A: Population PSTH and Onset Detection",
        subtitle="Omission-Aligned | Dashed lines indicate threshold crossing"
    )
    plotter_psth.set_axes("Time from Omission", "ms", "Firing Rate", "Hz")
    
    # Hierarchy Colors
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3", "#FFFFFF", "#AAAAAA", "#555555", "#333333", "#111111"]
    
    areas = list(results.keys())
    latencies = []
    valid_areas = []
    
    for i, area in enumerate(areas):
        data = results[area]
        t = data["times"]
        psth = data["psth"]
        lat = data["latency"]
        
        color = colors[i % len(colors)]
        plotter_psth.add_trace(go.Scatter(x=t, y=psth, name=area, line=dict(color=color)), name=area)
        
        if lat is not None:
            plotter_psth.add_xline(lat, f"{area} Onset", color=color, dash="dot")
            latencies.append(lat)
            valid_areas.append(area)
            
    plotter_psth.add_xline(0, "Omission", color="white", dash="dash")
    plotter_psth.save(output_dir, "f040_psth_onsets")
    
    # Plot B: Latency vs Hierarchy
    if latencies:
        plotter_lat = OmissionPlotter(
            title="Figure 40B: Omission Latency Hierarchy",
            subtitle="First significant FR deviation post-omission"
        )
        plotter_lat.set_axes("Brain Area", "Hierarchy", "Latency", "ms")
        
        plotter_lat.add_trace(go.Bar(
            x=valid_areas, 
            y=latencies,
            marker_color="#CFB87C",
            text=[f"{l:.1f}ms" for l in latencies],
            textposition="outside"
        ), name="Latency")
        
        plotter_lat.save(output_dir, "f040_latency_hierarchy")
