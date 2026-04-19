# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_pca_trajectories(results: dict):
    """
    Plots Figure 22: State-Space Trajectories (3D PCA).
    """
    # Note: OmissionPlotter currently creates a go.Figure() which defaults to 2D.
    # I'll create a 3D plot directly using go.Figure and update layout.
    
    for ses, data in results.items():
        fig = go.Figure()
        
        traj_std = data['std']
        traj_omit = data['omit']
        
        # Standard trajectory
        fig.add_trace(go.Scatter3d(
            x=traj_std[:, 0], y=traj_std[:, 1], z=traj_std[:, 2],
            mode='lines',
            line=dict(color='#8F00FF', width=4),
            name="Standard (AAAB)"
        ))
        
        # Omission trajectory
        fig.add_trace(go.Scatter3d(
            x=traj_omit[:, 0], y=traj_omit[:, 1], z=traj_omit[:, 2],
            mode='lines',
            line=dict(color='#FF1493', width=4),
            name="Omission (AXAB)"
        ))
        
        # Markers for key events
        # P1 Onset (Sample 1000)
        # Omission/P2 Onset (Sample 2031)
        fig.add_trace(go.Scatter3d(
            x=[traj_std[1000, 0], traj_omit[1000, 0]],
            y=[traj_std[1000, 1], traj_omit[1000, 1]],
            z=[traj_std[1000, 2], traj_omit[1000, 2]],
            mode='markers',
            marker=dict(size=8, color='black'),
            name="P1 Onset"
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[traj_std[2031, 0], traj_omit[2031, 0]],
            y=[traj_std[2031, 1], traj_omit[2031, 1]],
            z=[traj_std[2031, 2], traj_omit[2031, 2]],
            mode='markers',
            marker=dict(size=8, color='red'),
            name="P2 Onset / Omission"
        ))

        fig.update_layout(
            title=f"Figure 22: State-Space Trajectories (PCA) - Session {ses}",
            scene=dict(
                xaxis_title="PC1",
                yaxis_title="PC2",
                zaxis_title="PC3"
            ),
            template="plotly_white",
            modebar_add=['toImage']
        )

        filename = f"fig22_pca_trajectories_{ses}.html"
        fig.write_html(f"{output_dir}/{filename}")
        log.progress(f"Saved 3D PCA plot to {output_dir}/{filename}")
