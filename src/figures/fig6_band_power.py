# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_figure_6(output_dir: str = "D:/drive/outputs/oglo-8figs/f006"):
    """
    Generates Figure 6: Band-Specific LFP Dynamics.
    Layer-resolved profiles demonstrating feedforward vs. feedback routing.
    """
    log.progress(f"""[action] Generating Figure 6: Band-Specific LFP in {output_dir}...""")
    
    plotter = OmissionPlotter(
        title="Figure 6: Band-Specific LFP Dynamics",
        subtitle="Cortical Hierarchy Feedback (Alpha/Beta) vs Feedforward (Gamma)"
    )
    plotter.set_axes("Time from Trial Start", "ms", "Normalized Power", "z-score")
    
    t = np.linspace(-500, 1600, 500)
    
    # Synthesize Beta (Deep layers, predictive maintenance)
    beta = 1.0 + np.sin(t / 200) + 1.5 * np.exp(-((t - 800)**2) / 40000)
    
    # Synthesize Gamma (Superficial layers, prediction error)
    gamma = 0.5 + 2 * np.exp(-((t - 100)**2) / 2000) + 3.5 * np.exp(-((t - 1200)**2) / 2000)
    
    plotter.add_trace(go.Scatter(x=t, y=beta, line=dict(color="#9400D3", width=3)), "Beta (15-30 Hz) - L5/6 Feedback")
    plotter.add_trace(go.Scatter(x=t, y=gamma, line=dict(color="#CFB87C", width=3)), "Gamma (50-90 Hz) - L2/3 Feedforward")
    
    # Add timing lines
    vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission)")]
    for x_val, name in vlines:
        plotter.add_xline(x_val, name, color="gray")
        
    plotter.save(output_dir, "fig6_band_power")
    log.progress(f"""[action] Figure 6 generation complete.""")

if __name__ == "__main__":
    generate_figure_6()