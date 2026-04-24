# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_identity_decoding(times: np.ndarray, results: dict, output_dir: str):
    """
    Plots Figure 27: Omission Identity Decoding (A vs B).
    """
    plotter = OmissionPlotter(
        title="Figure 27: Omission Identity Decoding (Omit A vs Omit B)",
        subtitle="Population Decoder | Is the 'Surprise' stimulus-specific?"
    )
    plotter.set_axes("Time from P1 Onset", "ms", "Decoding Accuracy", "fraction")
    
    # Allowed color palette: [Red, Blue, Brown, Green, Orange, Purple, Yellow]
    colors = ["#FF0000", "#0000FF", "#A52A2A", "#008000", "#FFA500", "#800080", "#FFFF00"]
    times_adj = times - 1000
    
    for i, (area, data) in enumerate(results.items()):
        plotter.add_shaded_error_bar(
            times_adj, 
            data['mean'], 
            data['sem'], 
            area, 
            colors[i%len(colors)]
        )
        
    plotter.add_xline(0, "P1 Onset", color="black")
    plotter.add_xline(1031, "Omission Onset", color="red")
    plotter.add_yline(0.5, "Chance", color="gray", dash="dot")
    
    plotter.save(output_dir, "fig27_identity_decoding")
