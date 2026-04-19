# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_sfc_plv(results: dict, output_dir: str):
    """
    Plots Figure 7 SFC PLV spectra.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 7: {area} SFC (PLV)", 
            subtitle="Subsampling Corrected | Top 10 S+ vs O+ | Mean ± SEM"
        )
        plotter.set_axes("Frequency", "Hz", "Phase-Locking Value", "PLV")
        
        freqs = data['freqs']
        for name, spectra, color in [("S+ (Stimulus)", data['s_plus'], "#0000FF"), ("O+ (Omission)", data['o_plus'], "#9400D3")]:
            spectra = np.array(spectra)
            m = np.mean(spectra, axis=0)
            sem = np.std(spectra, axis=0) / np.sqrt(len(spectra))
            plotter.add_shaded_error_bar(freqs, m, sem, name, color)
            
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig7_sfc_spectrum_{area}")
