# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_cross_area_sfc(res: dict, output_dir: str):
    """
    Plots Cross-Area SFC Spectrum.
    """
    if not res: return
    plotter = OmissionPlotter(
        title=f"Figure: Cross-Area SFC ({res['pair']})",
        subtitle="Spectral coherence between single-unit spikes and distal LFP."
    )
    plotter.set_axes("Frequency", "Hz", "Coherence", "norm")
    plotter.add_trace(go.Scatter(x=res["freqs"], y=res["coh_mean"], name=res["pair"]), name=res["pair"])
    plotter.fig.update_xaxes(type="log")
    plotter.save(output_dir, f"fig_cross_area_sfc_{res['pair'].replace('->', '_to_')}")
