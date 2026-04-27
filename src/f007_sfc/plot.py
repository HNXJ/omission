import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np
import os

def plot_sfc_plv(results: dict, output_dir: str):
    """
    Plots Figure f007 SFC PLV spectra.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Aesthetic palette
    GOLD = "#CFB87C"
    PURPLE = "#9400D3"
    
    for area, data in results.items():
        stats = data['stats']
        proof_str = f"[{stats['test']}] {stats['tier']} (p={stats['p']:.2e}) {stats['stars']}"
        
        print(f"[action] Plotting SFC for {area}")
        plotter = OmissionPlotter(
            title=f"Figure f007: {area} Spike-Field Coherence {stats['stars']}",
            x_label="Frequency",
            y_label="Phase-Locking Value",
            subtitle=f"{proof_str} | Subsampling Corrected | Mean ± SEM",
            x_unit="Hz",
            y_unit="PLV"
        )
        
        freqs = data['freqs']
        for name, spectra, color in [("S+ (Stimulus)", data['s_plus'], GOLD), ("O+ (Omission)", data['o_plus'], PURPLE)]:
            spectra = np.array(spectra)
            if spectra.ndim == 2 and spectra.shape[0] > 0:
                m = np.mean(spectra, axis=0)
                sem = np.std(spectra, axis=0) / np.sqrt(len(spectra))
                plotter.add_shaded_error_bar(freqs, m, sem, error_lower=sem, name=name, color=color)
            
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        
        filename = f"f007_sfc_spectrum_{area}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html")
