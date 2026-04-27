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
    plotter = OmissionPlotter(title="Figure 18: Ghost Signals (Anticipatory Ramping)",
        x_label="Time", y_label="LFP (uV)",
        subtitle="Population Average of Ramping Units before Omission"
    )
    plotter.set_axes("Time from P1 Onset", "ms", "Firing Rate", "Hz")
    
    # Allowed color palette: [Red, Blue, Brown, Green, Orange, Purple, Yellow]
    colors = ["#FF0000", "#0000FF", "#A52A2A", "#008000", "#FFA500", "#800080", "#FFFF00"]
    
    for i, (area, data) in enumerate(results.items()):
        psth = data['avg_psth']
        sem = data['psth_sem']
        n_samples = len(psth)
        times = np.arange(0, n_samples)
        
        plotter.add_shaded_error_bar(
            times, 
            psth, 
            sem, 
            name=f"{area} (N={len(data['slopes'])})",
            color=colors[i % len(colors)]
        )
            
    # Add timing reference lines
    plotter.add_xline(1031, "Expected P2", color="violet")
    plotter.add_xline(531, "D1 Start", color="gray")

    # Fix legend overlap and margins
    plotter.fig.update_layout(
        margin=dict(t=120),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    plotter.save(output_dir, "fig18_ghost_signals")
