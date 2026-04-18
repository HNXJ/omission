# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_band_dynamics(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f006"):
    """
    Plots Figure 6 band dynamics.
    """
    from src.analysis.lfp.lfp_constants import GOLD, VIOLET
    colors = {"Theta": "#4B0082", "Alpha": "#0000FF", "Beta": VIOLET, "Gamma": GOLD}
    
    for area, res in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 6: {area} Band-Specific Omission Dynamics",
            subtitle="Relative Power (dB) | 0ms = Omission"
        )
        plotter.set_axes("Time from Omission", "ms", "Relative Power", "dB")
        
        for band_name, mean_trace in res["bands"].items():
            color = colors.get(band_name, GOLD)
            plotter.add_trace(go.Scatter(x=res["times"], y=mean_trace, mode='lines', line=dict(color=color, width=3)), name=band_name)
            
        plotter.add_xline(0, name="Omission", color="black")
        plotter.fig.update_xaxes(range=[-500, 1000])
        plotter.save(output_dir, f"fig6_band_power_local_{area}")
