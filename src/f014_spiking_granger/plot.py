# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_connectivity_delta(data_list: list, areas: list, output_dir: str):
    """
    Plots Figure 14 connectivity delta (AXAB - AAAB) aggregated across sessions.
    data_list: list of dicts with 'AXAB' and 'AAAB' tensors per session.
    """
    # Aggregate delta values
    deltas_beta = []
    deltas_gamma = []
    for session in data_list:
        if "AXAB" in session and "AAAB" in session:
            deltas_beta.append(session["AXAB"]["p2"]["Beta"] - session["AAAB"]["p2"]["Beta"])
            deltas_gamma.append(session["AXAB"]["p2"]["Gamma"] - session["AAAB"]["p2"]["Gamma"])
    
    if not deltas_beta: return
    
    mean_beta = np.mean(deltas_beta, axis=0)
    sem_beta = np.std(deltas_beta, axis=0) / np.sqrt(len(deltas_beta))
    
    mean_gamma = np.mean(deltas_gamma, axis=0)
    sem_gamma = np.std(deltas_gamma, axis=0) / np.sqrt(len(deltas_gamma))
    
    # Beta Plot
    plotter = OmissionPlotter(title="Figure 14: Beta Connectivity Delta", subtitle="Mean ± SEM (Omission Window p2)")
    # Since Connectivity delta is traditionally a heatmap, but shading is requested for averages:
    # If we need 1D profiles, we should project, but the requirement is to use add_shaded_error_bar.
    # Assuming standard projection or 1D representation.
    x_axis = np.arange(mean_beta.shape[0])
    plotter.add_shaded_error_bar(x=x_axis, y=mean_beta.mean(axis=1), error=sem_beta.mean(axis=1), name="ΔBeta MI")
    plotter.save(output_dir, "fig14_delta_mi_beta_p2_avg")
    
    # Gamma Plot
    plotter_g = OmissionPlotter(title="Figure 14: Gamma Connectivity Delta", subtitle="Mean ± SEM (Omission Window p2)")
    plotter_g.add_shaded_error_bar(x=x_axis, y=mean_gamma.mean(axis=1), error=sem_gamma.mean(axis=1), name="ΔGamma MI")
    plotter_g.save(output_dir, "fig14_delta_mi_gamma_p2_avg")
