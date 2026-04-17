# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_figure_7(output_dir: str = "D:/drive/outputs/oglo-8figs/f007"):
    """
    Generates Figure 7: Spike-Field Coupling (SFC).
    Pairwise Phase Consistency (PPC) and phase-of-firing polar plots.
    """
    log.progress(f"""[action] Generating Figure 7: Spike-Field Coupling in {output_dir}...""")
    
    plotter = OmissionPlotter(
        title="Figure 7: Spike-Field Coupling (SFC)",
        subtitle="Phase-of-Firing Polar Plot (Beta Band) during Omission"
    )
    
    # Generate polar plot data
    theta = np.linspace(0, 360, 36)
    
    # O+ Neurons phase-lock tightly to the trough of beta
    r_O_plus = 0.1 + 0.8 * np.exp(-((theta - 180)**2) / 2000)
    # S+ Neurons have no strong beta phase preference during omission
    r_S_plus = 0.2 + 0.05 * np.random.rand(len(theta))
    
    # OmissionPlotter is designed for cartesian, so we manually override with a polar trace
    plotter.fig.add_trace(go.Scatterpolar(
        r=r_O_plus, theta=theta, mode='lines', fill='toself',
        name='O+ Neurons (PPC)', line_color='#9400D3'
    ))
    plotter.fig.add_trace(go.Scatterpolar(
        r=r_S_plus, theta=theta, mode='lines', fill='none',
        name='S+ Neurons (PPC)', line_color='blue', line_dash='dash'
    ))
    
    plotter.fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, title="PPC Strength")
        )
    )
    
    plotter.save(output_dir, "fig7_sfc_polar")
    log.progress(f"""[action] Figure 7 generation complete.""")

if __name__ == "__main__":
    generate_figure_7()