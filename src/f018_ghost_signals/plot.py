# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_ghost_signals(results: dict, output_dir: str):
    """
    Plots Figure 18: Ghost Signals (Anticipatory Ramping).
    results: {area: {'slopes': [], 'avg_psth': (time,)}}
    """
    plotter = OmissionPlotter(
        title="Figure 18: Ghost Signals (Anticipatory Ramping)",
        subtitle="Population Average of Ramping Units before Omission"
    )
    plotter.set_axes("Time from P1 Onset", "ms", "Firing Rate", "Hz")
    
    # Madelane Golden Dark inspired color palette
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    
    times = np.arange(0, 6000)
    
    for i, (area, data) in enumerate(results.items()):
        psth = data['avg_psth']
        sem = data['psth_sem']
        
        plotter.add_shaded_error_bar(
            times, 
            psth, 
            sem, 
            f"{area} (N={len(data['slopes'])})",
            colors[i % len(colors)]
        )
            
    # Add timing reference lines
    plotter.add_xline(1031, "Expected P2", color="violet")
    plotter.add_xline(531, "D1 Start", color="gray")

    plotter.save(output_dir, "fig18_ghost_signals")
