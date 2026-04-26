import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import os
import numpy as np

def plot_granger_causality(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    areas = list(results.keys())
    if not areas:
        log.warning("No Granger results to plot.")
        return
        
    stim_ff = [results[a]["stim"]["ff"] for a in areas]
    stim_fb = [results[a]["stim"]["fb"] for a in areas]
    
    omit_ff = [results[a]["omit"]["ff"] for a in areas]
    omit_fb = [results[a]["omit"]["fb"] for a in areas]
    
    # 1. Stimulus vs Omission Bar Plot
    plotter = OmissionPlotter(
        title="Figure f029: Effective Connectivity (Granger Causality)",
        subtitle="Directed Influence: Feedforward (V1 -> Area) vs Feedback (Area -> V1)"
    )
    plotter.set_axes("Cortical Area", "", "Granger F-Statistic", "")
    
    plotter.add_trace(go.Bar(name="Stimulus (FF)", x=areas, y=stim_ff, marker_color="#0000FF"))
    plotter.add_trace(go.Bar(name="Stimulus (FB)", x=areas, y=stim_fb, marker_color="#4B0082"))
    
    plotter.add_trace(go.Bar(name="Omission (FF)", x=areas, y=omit_ff, marker_color="#CFB87C"))
    plotter.add_trace(go.Bar(name="Omission (FB)", x=areas, y=omit_fb, marker_color="#D55E00"))
    
    plotter.fig.update_layout(barmode='group')
    plotter.save(output_dir, "f029_effective_connectivity_summary")
    
    # 2. Reversal Index Plot (FB - FF)
    plotter_rev = OmissionPlotter(
        title="Figure f029: Feedback Reversal Index",
        subtitle="Omission (FB - FF) minus Stimulus (FB - FF)"
    )
    plotter_rev.set_axes("Cortical Area", "", "Reversal Index (\u0394 F)", "")
    
    rev_index = [(omit_fb[i] - omit_ff[i]) - (stim_fb[i] - stim_ff[i]) for i in range(len(areas))]
    colors = ["#D55E00" if v > 0 else "#0000FF" for v in rev_index]
    
    plotter_rev.add_trace(go.Bar(name="Reversal Index", x=areas, y=rev_index, marker_color=colors))
    plotter_rev.save(output_dir, "f029_feedback_reversal")
    
    log.progress("Effective Connectivity plots saved.")
