# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_population_manifolds(results: dict, output_dir: str):
    """
    Plots Figure 4 3D population manifolds with bootstrapped CI tubes.
    """
    for area, data in results.items():
        print(f"""[action] Plotting CI tubes for area {area}""")
        plotter = OmissionPlotter(
            title=f"Figure 4: {area} Population State-Space Dynamics",
            subtitle="3D PCA Trajectories: Standard vs. Omission (with 95% CI)"
        )
        plotter.fig.update_layout(scene=dict(xaxis_title="PC1", yaxis_title="PC2", zaxis_title="PC3"))
        
        # Add Mean Traces
        plotter.fig.add_trace(go.Scatter3d(
            x=data['traj_aaab'][:, 0], y=data['traj_aaab'][:, 1], z=data['traj_aaab'][:, 2],
            mode='lines', line=dict(color='black', width=4, dash='dash'), name='Standard (AAAB)'
        ))
        plotter.fig.add_trace(go.Scatter3d(
            x=data['traj_axab'][:, 0], y=data['traj_axab'][:, 1], z=data['traj_axab'][:, 2],
            mode='lines', line=dict(color='#9400D3', width=6), name='Omission (AXAB)'
        ))
        
        # Add CI Tubes (using low-opacity ribbon)
        for name, ci, color in [("Standard", data['ci_aaab'], "gray"), ("Omission", data['ci_axab'], "purple")]:
            plotter.fig.add_trace(go.Scatter3d(
                x=ci[0, :, 0], y=ci[0, :, 1], z=ci[0, :, 2],
                mode='lines', line=dict(color=color, width=1), opacity=0.3, showlegend=False
            ))
            plotter.fig.add_trace(go.Scatter3d(
                x=ci[1, :, 0], y=ci[1, :, 1], z=ci[1, :, 2],
                mode='lines', line=dict(color=color, width=1), opacity=0.3, showlegend=False
            ))
            
        plotter.save(output_dir, f"fig4_population_manifold_{area}")
        print(f"""[action] Saved Figure 4 for {area}""")
