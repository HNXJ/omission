# beta
import plotly.graph_objects as go
from src.analysis.io.logger import log
import numpy as np

def plot_pca_trajectories(results: dict, output_dir: str):
    """
    Plots Figure 22: State-Space Trajectories (3D PCA).
    Uses Madelane Golden Dark aesthetic: #CFB87C (Standard) / #9400D3 (Omission).
    """
    GOLD = "#CFB87C"
    PURPLE = "#9400D3"
    
    for ses, data in results.items():
        print(f"[action] Plotting 3D PCA for session {ses}")
        fig = go.Figure()
        
        traj_std = data['std']
        traj_omit = data['omit']
        
        # Standard trajectory
        fig.add_trace(go.Scatter3d(
            x=traj_std[:, 0], y=traj_std[:, 1], z=traj_std[:, 2],
            mode='lines',
            line=dict(color=GOLD, width=6),
            name="Standard (AAAB)"
        ))
        
        # Omission trajectory
        fig.add_trace(go.Scatter3d(
            x=traj_omit[:, 0], y=traj_omit[:, 1], z=traj_omit[:, 2],
            mode='lines',
            line=dict(color=PURPLE, width=6),
            name="Omission (AXAB)"
        ))
        
        # Markers for key events (aligned to p1)
        # P1 Onset is sample 1000
        # P2/Omission is sample 1000 + 1031 (approx 2031) - assuming 1031ms SOA
        
        p1_idx = 1000
        p2_idx = 2031
        
        # Add a marker for P1 start
        if p1_idx < traj_std.shape[0]:
            fig.add_trace(go.Scatter3d(
                x=[traj_std[p1_idx, 0]],
                y=[traj_std[p1_idx, 1]],
                z=[traj_std[p1_idx, 2]],
                mode='markers',
                marker=dict(size=10, color='black', symbol='diamond'),
                name="P1 Onset (Std)"
            ))
            fig.add_trace(go.Scatter3d(
                x=[traj_omit[p1_idx, 0]],
                y=[traj_omit[p1_idx, 1]],
                z=[traj_omit[p1_idx, 2]],
                mode='markers',
                marker=dict(size=10, color='black', symbol='circle'),
                name="P1 Onset (Omit)"
            ))
            
        # Add a marker for P2/Omission start
        if p2_idx < traj_std.shape[0]:
            fig.add_trace(go.Scatter3d(
                x=[traj_std[p2_idx, 0]],
                y=[traj_std[p2_idx, 1]],
                z=[traj_std[p2_idx, 2]],
                mode='markers',
                marker=dict(size=12, color=GOLD, symbol='circle', line=dict(color='black', width=2)),
                name="P2 Onset (Std)"
            ))
            fig.add_trace(go.Scatter3d(
                x=[traj_omit[p2_idx, 0]],
                y=[traj_omit[p2_idx, 1]],
                z=[traj_omit[p2_idx, 2]],
                mode='markers',
                marker=dict(size=12, color=PURPLE, symbol='circle', line=dict(color='black', width=2)),
                name="Omission Onset"
            ))

        var_exp = data['explained_var']
        title_text = (
            f"<b>Figure 22: State-Space Trajectories (PCA) - Session {ses}</b><br>"
            f"<sup>Variance Explained: PC1={var_exp[0]:.1%}, PC2={var_exp[1]:.1%}, PC3={var_exp[2]:.1%}</sup>"
        )

        fig.update_layout(
            title=dict(text=title_text, x=0.5, xanchor='center'),
            scene=dict(
                xaxis_title="PC1",
                yaxis_title="PC2",
                zaxis_title="PC3",
                xaxis=dict(backgroundcolor="white", gridcolor="lightgray", showbackground=True, zerolinecolor="gray"),
                yaxis=dict(backgroundcolor="white", gridcolor="lightgray", showbackground=True, zerolinecolor="gray"),
                zaxis=dict(backgroundcolor="white", gridcolor="lightgray", showbackground=True, zerolinecolor="gray"),
            ),
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            modebar_add=['toImage'],
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=0, r=0, b=0, t=80)
        )

        import os
        os.makedirs(output_dir, exist_ok=True)
        filename = f"fig22_pca_trajectories_{ses}.html"
        filepath = os.path.join(output_dir, filename)
        fig.write_html(filepath, include_plotlyjs="cdn")
        print(f"[action] Saved 3D PCA plot to {filepath}")
        log.progress(f"Saved 3D PCA plot to {filepath}")
