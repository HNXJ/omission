# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_area_psths(results: dict, output_dir: str):
    """
    Plots Figure 3 area PSTHs.
    """
    t_local = np.linspace(-1000, 1000, 2000)
    
    for area, data in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 3: {area} Omission-Local PSTH",
            subtitle=f"n={data['n_units']} units | Mean ± SEM | 0ms = Omission Onset"
        )
        plotter.set_axes("Time from Omission", "ms", "Firing Rate", "Hz")
        
        plotter.add_shaded_error_bar(t_local, data['aaab'], data['aaab_sem'], "Standard (AAAB)", "#000000")
        plotter.add_shaded_error_bar(t_local, data['axab'], data['axab_sem'], "Omission (AXAB)", "#9400D3")
        
        plotter.add_xline(0, "Omission/Stim 2", color="red")
        plotter.fig.update_xaxes(range=[-500, 1000])
        plotter.save(output_dir, f"fig3_psth_local_{area}")
