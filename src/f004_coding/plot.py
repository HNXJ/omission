# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_population_manifolds(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f004"):
    """
    Plots Figure 4 3D population manifolds.
    """
    for area, data in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 4: {area} Population State-Space Dynamics",
            subtitle="3D PCA Trajectories: Standard (AAAB) vs. Omission (AXAB)"
        )
        plotter.fig.update_layout(scene=dict(xaxis_title="PC1", yaxis_title="PC2", zaxis_title="PC3"))
        
        plotter.fig.add_trace(go.Scatter3d(
            x=data['traj_aaab'][:, 0], y=data['traj_aaab'][:, 1], z=data['traj_aaab'][:, 2],
            mode='lines', line=dict(color='black', width=4, dash='dash'), name='Standard (AAAB)'
        ))
        plotter.fig.add_trace(go.Scatter3d(
            x=data['traj_axab'][:, 0], y=data['traj_axab'][:, 1], z=data['traj_axab'][:, 2],
            mode='lines', line=dict(color='#9400D3', width=6), name='Omission (AXAB)'
        ))
        plotter.save(output_dir, f"fig4_population_manifold_{area}")
