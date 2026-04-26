import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np
import os

def plot_sfc_delta(results: dict, output_dir: str):
    """
    Plots continuous Delta SFC.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for area, data in results.items():
        plotter = OmissionPlotter(
            title=f"Figure f010: {area} Delta SFC", 
            subtitle=f"Continuous 2-4 Hz Phase-Locking Value | N={data['n_units']} units"
        )
        plotter.set_axes("Time from Omission", "ms", "Delta SFC", "PLV")
        
        times = data["times"]
        ax_mean = data["ax_mean"]
        ax_sem = data["ax_sem"]
        aa_mean = data["aa_mean"]
        aa_sem = data["aa_sem"]
        
        # AAAB = Standard
        plotter.add_shaded_error_bar(times, aa_mean, aa_sem, error_lower=aa_sem, name="Standard (AAAB)", color="#8F00FF")
        # AXAB = Omission
        plotter.add_shaded_error_bar(times, ax_mean, ax_sem, error_lower=ax_sem, name="Omission (AXAB)", color="#FF1493")
        
        plotter.add_xline(0, "Omission Onset", color="black")
        plotter.add_xline(-1031, "P1 Onset", color="gray", dash="dot")
        
        filename = f"f010_sfc_delta_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html and SVG.")
