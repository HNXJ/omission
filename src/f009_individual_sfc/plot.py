# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_individual_sfc(results: dict, output_dir: str):
    """
    Plots Figure 9 individual unit SFC spectra.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(title=f"Figure 9: {area} Individual SFC", subtitle="Top S+ (Stimulus) and O+ (Omission) PLV")
        plotter.set_axes("Frequency", "Hz", "PLV", "Magnitude")
        
        freqs = data['freqs']
        
        # S+ (Stimulus)
        s_plus_mean = np.mean(data['s_plus'], axis=0)
        s_plus_sem = np.std(data['s_plus'], axis=0) / np.sqrt(len(data['s_plus']))
        plotter.add_shaded_error_bar(freqs, s_plus_mean, s_plus_sem, name="S+ (Stimulus)", color="#0000FF")
        print(f"""[action] Added S+ shaded error bar (Blue) for {area}""")

        # O+ (Omission)
        o_plus_mean = np.mean(data['o_plus'], axis=0)
        o_plus_sem = np.std(data['o_plus'], axis=0) / np.sqrt(len(data['o_plus']))
        plotter.add_shaded_error_bar(freqs, o_plus_mean, o_plus_sem, name="O+ (Omission)", color="#9400D3")
        print(f"""[action] Added O+ shaded error bar (Purple) for {area}""")
            
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig9_individual_sfc_{area}")
