# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_figure_4(output_dir: str = "D:/drive/outputs/oglo-8figs/f004"):
    """
    Generates Figure 4: Population State-Space Dynamics.
    3D PCA trajectories comparing stimulus vs. omission paths.
    """
    log.progress(f"""[action] Generating Figure 4: Population State-Space in {output_dir}...""")
    
    plotter = OmissionPlotter(
        title="Figure 4: Population State-Space Dynamics",
        subtitle="3D PCA Trajectories: Stimulus vs. Omission"
    )
    
    # 3D axes are configured within the layout, so we skip plotter.set_axes and set them manually.
    plotter.fig.update_layout(
        scene=dict(
            xaxis_title="PC 1 (Arbitrary Units)",
            yaxis_title="PC 2 (Arbitrary Units)",
            zaxis_title="PC 3 (Arbitrary Units)"
        )
    )
    
    # Generate synthetic 3D spiral trajectories
    t = np.linspace(0, 4*np.pi, 200)
    
    # Stimulus Trajectory (Standard AAAB)
    x_stim = np.cos(t) * (1 + 0.1*t)
    y_stim = np.sin(t) * (1 + 0.1*t)
    z_stim = 0.5 * t
    
    # Omission Trajectory (AXAB) diverges at t > 2*pi
    divergence_idx = len(t) // 2
    x_omi = np.copy(x_stim)
    y_omi = np.copy(y_stim)
    z_omi = np.copy(z_stim)
    
    t_div = t[divergence_idx:]
    x_omi[divergence_idx:] += 2 * (1 - np.cos(t_div - t_div[0]))
    z_omi[divergence_idx:] += 1.5 * (t_div - t_div[0])
    
    plotter.fig.add_trace(go.Scatter3d(
        x=x_stim, y=y_stim, z=z_stim, mode='lines',
        line=dict(color='black', width=4, dash='dash'), name='Standard (AAAB)'
    ))
    
    plotter.fig.add_trace(go.Scatter3d(
        x=x_omi, y=y_omi, z=z_omi, mode='lines',
        line=dict(color='#9400D3', width=6), name='Omission (AXAB)'
    ))
    
    plotter.save(output_dir, "fig4_population_manifold")
    log.progress(f"""[action] Figure 4 generation complete.""")

if __name__ == "__main__":
    generate_figure_4()