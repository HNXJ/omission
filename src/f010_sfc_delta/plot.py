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
        
        # Mean Delta + SEM
        mean_delta = np.mean(data['deltas'], axis=0)
        sem_delta = np.std(data['deltas'], axis=0) / np.sqrt(len(data['deltas']))
        plotter.add_shaded_error_bar(freqs, mean_delta, sem_delta, name="Mean Delta", color="#9400D3")
        print(f"""[action] Added Mean Delta shaded error bar (Purple) for {area}""")

        plotter.fig.add_hline(y=0, line_dash="dash", line_color="black")
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig10_sfc_delta_{area}")
