# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_sfc_plv(results: dict, output_dir: str):
    """
    Plots Figure 7 SFC PLV spectra.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(title=f"Figure 7: {area} SFC (PLV)", subtitle="Subsampling Corrected: Top 10 S+ vs O+")
        plotter.set_axes("Frequency", "Hz", "Phase-Locking Value", "PLV")
        
        freqs = data['freqs']
        for name, spectra, color in [("S+ (Stimulus)", data['s_plus'], "#CFB87C"), ("O+ (Omission)", data['o_plus'], "#9400D3")]:
            m = np.mean(spectra, axis=0)
            plotter.add_trace(go.Scatter(x=freqs, y=m, mode='lines', line=dict(color=color, width=3)), name=name)
            
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig7_sfc_spectrum_{area}")
