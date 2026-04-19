# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_rnn_modeling(h_std, h_omit, error, output_dir):
    """
    Plots Figure 31: RNN Modeling Results.
    """
    # 1. State Trajectories
    plotter_state = OmissionPlotter(
        title="Figure 31A: RNN Hidden State (Unit 0)",
        subtitle="Standard (A-A-A-B) vs Omission (A-X-A-B)"
    )
    plotter_state.set_axes("Time Step", "idx", "Hidden Activation", "tanh")
    
    t = np.arange(len(h_std))
    plotter_state.add_trace(go.Scatter(x=t, y=h_std[:, 0], name="Standard (Unit 0)", line=dict(color="black", dash="dash")), name="Standard")
    plotter_state.add_trace(go.Scatter(x=t, y=h_omit[:, 0], name="Omission (Unit 0)", line=dict(color="#8F00FF")), name="Omission")
    plotter_state.save(output_dir, "fig31A_rnn_state")
    
    # 2. Prediction Error (Distance)
    plotter_err = OmissionPlotter(
        title="Figure 31B: RNN State Divergence (PE)",
        subtitle="Euclidean Distance | Standard vs Omission State"
    )
    plotter_err.set_axes("Time Step", "idx", "State Distance", "norm")
    plotter_err.add_trace(go.Scatter(x=t, y=error, fill='tozeroy', line=dict(color="#FF1493")), name="Prediction Error")
    plotter_err.add_xline(5, "Omission Event", color="red")
    plotter_err.save(output_dir, "fig31B_rnn_divergence")
