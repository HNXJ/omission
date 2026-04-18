# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_area_psths(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f003"):
    """
    Plots Figure 3 area PSTHs.
    """
    t_local = np.linspace(-1000, 1000, 2000)
    
    for area, data in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 3: {area} Omission-Local PSTH",
            subtitle=f"n={data['n_units']} units | 0ms = Omission Onset"
        )
        plotter.set_axes("Time from Omission", "ms", "Firing Rate", "Hz")
        
        plotter.add_trace(go.Scatter(x=t_local, y=data['aaab'], line=dict(color="black", width=2, dash="dash")), "Standard (AAAB)")
        plotter.add_trace(go.Scatter(x=t_local, y=data['axab'], line=dict(color="#9400D3", width=3)), "Omission (AXAB)")
        
        plotter.add_xline(0, "Omission/Stim 2", color="red")
        plotter.fig.update_xaxes(range=[-500, 1000])
        plotter.save(output_dir, f"fig3_psth_local_{area}")
