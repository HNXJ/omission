# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_individual_sfc(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f009"):
    """
    Plots Figure 9 individual unit SFC spectra.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(title=f"Figure 9: {area} Individual SFC", subtitle="Top S+ (Stimulus) and O+ (Omission) PLV")
        plotter.set_axes("Frequency", "Hz", "PLV", "Magnitude")
        
        freqs = data['freqs']
        for i, plv in enumerate(data['s_plus']):
            plotter.add_trace(go.Scatter(x=freqs, y=plv, line=dict(color="rgba(207,184,124,0.3)", width=1), showlegend=False), name=f"S+_{i}")
        for i, plv in enumerate(data['o_plus']):
            plotter.add_trace(go.Scatter(x=freqs, y=plv, line=dict(color="rgba(148,0,211,0.3)", width=1), showlegend=False), name=f"O+_{i}")
            
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig9_individual_sfc_{area}")
