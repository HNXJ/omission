# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_pac_summary(results: dict, output_dir: str):
    """
    Plots Figure 19: PAC (Modulation Index) across Areas.
    results: {area: [mi_values]}
    """
    plotter = OmissionPlotter(
        title="Figure 19: Phase-Amplitude Coupling (PAC)",
        subtitle="Modulation Index (Tort 2010) | Phase: Beta (13-30Hz), Amp: Gamma (35-80Hz)"
    )
    plotter.set_axes("Brain Area", "Index", "Modulation Index (MI)", "units")
    
    areas = list(results.keys())
    means = [np.mean(results[a]) if results[a] else 0 for a in areas]
    stds = [np.std(results[a]) if results[a] else 0 for a in areas]
    
    # Allowed color palette: [Red, Blue, Brown, Green, Orange, Purple, Yellow]
    colors = ["#FF0000", "#0000FF", "#A52A2A", "#008000", "#FFA500", "#800080", "#FFFF00"]
    
    plotter.add_trace(
        go.Bar(
            x=areas, 
            y=means,
            error_y=dict(type='data', array=stds, visible=True),
            marker_color=colors[:len(areas)]
        ),
        name="PAC Intensity"
    )

    plotter.save(output_dir, "fig19_pac_analysis")
