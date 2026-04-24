import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_area_psths(results: dict, output_dir: str):
    """
    Plots area PSTHs for Standard vs Omission.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    t_local = np.linspace(-1000, 1000, 2000) # Since align_to="omission" uses 2000 samples [-1000, +1000]
    
    for area, data in results.items():
        print(f"[action] Plotting PSTH for {area}")
        plotter = OmissionPlotter(
            title=f"Figure f002: {area} Omission-Local PSTH",
            subtitle=f"n={data['n_units']} units | Mean ± SEM | 0ms = Omission Onset"
        )
        plotter.set_axes("Time from Omission", "ms", "Firing Rate", "Hz")
        
        # Omission Plotter Madelane Golden Dark Theme
        GOLD = "#CFB87C"
        PURPLE = "#9400D3"
        
        plotter.add_shaded_error_bar(t_local, data['aaab'], data['aaab_sem'], error_lower=data['aaab_sem'], name="Standard (AAAB)", color=GOLD)
        plotter.add_shaded_error_bar(t_local, data['axab'], data['axab_sem'], error_lower=data['axab_sem'], name="Omission (AXAB)", color=PURPLE)
        
        plotter.add_xline(0, "Omission Onset", color="red", dash="dash")
        plotter.fig.update_xaxes(range=[-500, 1000])
        
        filename = f"f002_psth_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html")
