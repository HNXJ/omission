# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_sfc_delta(results: dict, output_dir: str):
    """
    Plots Figure 10 SFC Delta spectra.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(title=f"Figure 10: {area} SFC Delta", subtitle="Omission PLV - Stimulus PLV")
        plotter.set_axes("Frequency", "Hz", "PLV Delta", "Magnitude")
        
        freqs = data['freqs']
        for i, delta in enumerate(data['deltas']):
            plotter.add_trace(go.Scatter(x=freqs, y=delta, line=dict(color="rgba(148,0,211,0.2)", width=1), showlegend=False), name=f"Delta_{i}")
            
        mean_delta = np.mean(data['deltas'], axis=0)
        plotter.add_trace(go.Scatter(x=freqs, y=mean_delta, line=dict(color="#9400D3", width=4)), name="Mean Delta")
        plotter.fig.add_hline(y=0, line_dash="dash", line_color="black")
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig10_sfc_delta_{area}")
