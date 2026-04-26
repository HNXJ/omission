# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_pupil_surprise(results: dict, output_dir: str):
    """
    Plots Figure 21: Pupil Surprise.
    results: {session: { 'omit': (time,), 'std': (time,) }}
    """
    plotter = OmissionPlotter(
        title="Figure 21: Pupil Diameter Response to Omission",
        subtitle="Arousal proxy for unexpected violations | Baseline: [-500, 0]ms"
    )
    plotter.set_axes("Time from P1 Onset", "ms", "Δ Pupil Diameter", "Z-score")
    
    # Grand average across sessions
    omit_all = np.array([v['omit'] for v in results.values()])
    std_all = np.array([v['std'] for v in results.values()])
    
    omit_mean = np.mean(omit_all, axis=0)
    omit_sem = np.std(omit_all, axis=0) / np.sqrt(len(omit_all))
    
    std_mean = np.mean(std_all, axis=0)
    std_sem = np.std(std_all, axis=0) / np.sqrt(len(std_all))
    
    times = np.arange(0, 6000) - 1000 # Align to P1 onset at 0ms
    
    plotter.add_shaded_error_bar(times, omit_mean, omit_sem, name="Omission (AXAB)", color="#FF1493")
    plotter.add_shaded_error_bar(times, std_mean, std_sem, name="Standard (AAAB)", color="#8F00FF")
    
    # Add timing reference lines
    plotter.add_xline(0, "P1 Onset", color="black")
    plotter.add_xline(1031, "Omission Onset", color="red")

    plotter.save(output_dir, "fig21_pupil_surprise")
