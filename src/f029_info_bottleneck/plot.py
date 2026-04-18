# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_information_bottleneck(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f029"):
    """
    Plots Figure 29: Information Bottleneck (Past vs Label Information).
    """
    plotter = OmissionPlotter(
        title="Figure 29: Information Bottleneck",
        subtitle="Retention (Past) vs New Signal (Identity) | Hierarchy Profile"
    )
    plotter.set_axes("Area", "Hierarchy", "Mutual Information (bits)", "bits")
    
    areas = list(results.keys())
    past_mi = [results[area]['past_mi'] for area in areas]
    label_mi = [results[area]['label_mi'] for area in areas]
    
    plotter.add_trace(go.Bar(x=areas, y=past_mi, name="Retention MI(Past; Present)", marker_color="#8F00FF"), name="Retention")
    plotter.add_trace(go.Bar(x=areas, y=label_mi, name="Signal MI(Label; Present)", marker_color="#CFB87C"), name="Signal")
    
    plotter.fig.update_layout(barmode='group')
    plotter.save(output_dir, "fig29_info_bottleneck")
