# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_fano_factor(results: dict, output_dir: str):
    """
    Plots Figure 24: Fano Factor Dynamics.
    """
    plotter = OmissionPlotter(
        title="Figure 24: Fano Factor Variability Dynamics",
        subtitle="Population Average (Sliding 50ms window) | Contrast: Variability Quenching"
    )
    plotter.set_axes("Time from P1 Onset", "ms", "Fano Factor (Var/Mean)", "ratio")
    
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    times = np.arange(0, 6000) - 1000
    
    for i, (area, data) in enumerate(results.items()):
        plotter.add_shaded_error_bar(
            times, 
            data['mean'], 
            data['sem'], 
            area, 
            colors[i % len(colors)]
        )
        
    plotter.add_xline(0, "P1 Onset", color="black")
    plotter.add_xline(1031, "Omission Onset", color="red")
    plotter.add_yline(1.0, "Poisson Baseline", color="gray", dash="dot")

    plotter.save(output_dir, "fig24_fano_factor")
