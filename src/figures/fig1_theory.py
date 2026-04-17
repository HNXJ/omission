# core
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_figure_1(output_dir: str = "D:/drive/outputs/oglo-8figs/f001"):
    """
    Generates Figure 1: Theory Schematic.
    Focuses on predictive routing / signal-noise routing models (L2/3 vs. L5/6),
    emphasizing the omission window as the key test of internally driven prediction errors.
    """
    log.progress(f"""[action] Generating Figure 1: Theory Schematic in {output_dir}...""")
    
    # Initialize the plotter
    plotter = OmissionPlotter(
        title="Figure 1: Predictive Routing Theory Schematic",
        subtitle="Canonical L2/3 vs L5/6 Signal & Prediction Error Routing"
    )
    
    # Set invisible axes for a schematic
    plotter.fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, range=[0, 10])
    plotter.fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, range=[0, 10])
    plotter.set_axes(x_label="", x_unit="Arb", y_label="", y_unit="Arb")
    
    # Draw L2/3 Box (Superficial)
    plotter.fig.add_shape(type="rect", x0=2, y0=6, x1=4, y1=9,
                          line=dict(color="#CFB87C", width=3), fillcolor="rgba(207, 184, 124, 0.2)")
    plotter.fig.add_annotation(x=3, y=7.5, text="<b>Layer 2/3</b><br>Prediction Errors (Gamma)", showarrow=False, font=dict(size=14))
    
    # Draw L5/6 Box (Deep)
    plotter.fig.add_shape(type="rect", x0=2, y0=1, x1=4, y1=4,
                          line=dict(color="#9400D3", width=3), fillcolor="rgba(148, 0, 211, 0.2)")
    plotter.fig.add_annotation(x=3, y=2.5, text="<b>Layer 5/6</b><br>Internal Predictions (Alpha/Beta)", showarrow=False, font=dict(size=14))
    
    # Draw Stimulus / Omission input
    plotter.fig.add_annotation(x=1, y=5, text="<b>Sensory Input</b><br>(Stimulus / Omission)", showarrow=True, arrowhead=2, ax=30, ay=0, arrowcolor="black", font=dict(size=12))
    
    # Add routing arrows
    plotter.fig.add_annotation(x=3.5, y=5.8, ax=3.5, ay=4.2, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowcolor="#9400D3", text="Feedback (Alpha/Beta)")
    plotter.fig.add_annotation(x=2.5, y=4.2, ax=2.5, ay=5.8, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowcolor="#CFB87C", text="Feedforward (Gamma)")
    
    # Save the figure adhering to the Kaleido-Free HTML-only mandate
    plotter.save(output_dir, "fig1_theory_schematic")
    log.progress(f"""[action] Figure 1 generation complete.""")

if __name__ == "__main__":
    generate_figure_1()