# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def plot_theory_schematic(output_dir: str):
    """
    Plots the Figure 1 theory schematic.
    """
    log.progress(f"[action] Plotting Figure 1 Schematic...")
    plotter = OmissionPlotter(
        "Figure 1: Predictive Routing Theory Schematic",
        "",
        "",
        subtitle="Canonical L2/3 vs L5/6 Signal & Prediction Error Routing",
        x_unit="Arb",
        y_unit="Arb"
    )
    
    plotter.fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, range=[0, 10])
    plotter.fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, range=[0, 10])
    
    # Draw L2/3 Box (Superficial)
    plotter.fig.add_shape(type="rect", x0=2, y0=6, x1=4, y1=9,
                          line=dict(color="#CFB87C", width=3), fillcolor="rgba(207, 184, 124, 0.2)")
    plotter.fig.add_annotation(x=3, y=7.5, text="<b>Layer 2/3</b><br>Prediction Errors (Gamma)", showarrow=False, font=dict(size=14))
    
    # Draw L5/6 Box (Deep)
    plotter.fig.add_shape(type="rect", x0=2, y0=1, x1=4, y1=4,
                          line=dict(color="#9400D3", width=3), fillcolor="rgba(148, 0, 211, 0.2)")
    plotter.fig.add_annotation(x=3, y=2.5, text="<b>Layer 5/6</b><br>Internal Predictions (Alpha/Beta)", showarrow=False, font=dict(size=14))
    
    # Sensory input
    plotter.fig.add_annotation(x=1, y=5, text="<b>Sensory Input</b><br>(Stimulus / Omission)", showarrow=True, arrowhead=2, ax=30, ay=0, arrowcolor="black", font=dict(size=12))
    
    # Routing arrows
    plotter.fig.add_annotation(x=3.5, y=5.8, ax=3.5, ay=4.2, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowcolor="#9400D3", text="Feedback (Alpha/Beta)")
    plotter.fig.add_annotation(x=2.5, y=4.2, ax=2.5, ay=5.8, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowcolor="#CFB87C", text="Feedforward (Gamma)")
    
    plotter.save(output_dir, "fig1_theory_schematic")
