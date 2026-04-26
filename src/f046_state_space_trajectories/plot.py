import plotly.graph_objects as go
from src.analysis.io.logger import log
import os
import numpy as np

def plot_trajectories(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    if not results:
        log.warning("No State-Space Trajectory results to plot.")
        return
        
    for area, data in results.items():
        traj_aa = data["traj_aa"]
        traj_ax = data["traj_ax"]
        var = data["var_explained"]
        n_units = data["n_units"]
        
        fig = go.Figure()
        
        # Standard Trajectory (AAAB)
        fig.add_trace(go.Scatter3d(
            x=traj_aa[:, 0], y=traj_aa[:, 1], z=traj_aa[:, 2],
            mode='lines',
            line=dict(color='#8F00FF', width=5),
            name='Standard (AAAB)'
        ))
        
        # Omission Trajectory (AXAB)
        fig.add_trace(go.Scatter3d(
            x=traj_ax[:, 0], y=traj_ax[:, 1], z=traj_ax[:, 2],
            mode='lines',
            line=dict(color='#FF1493', width=5),
            name='Omission (AXAB)'
        ))
        
        # Mark omission onset (index 1000)
        idx_onset = 1000
        fig.add_trace(go.Scatter3d(
            x=[traj_aa[idx_onset, 0]], y=[traj_aa[idx_onset, 1]], z=[traj_aa[idx_onset, 2]],
            mode='markers',
            marker=dict(size=8, color='black', symbol='diamond'),
            name='Omission Onset'
        ))
        fig.add_trace(go.Scatter3d(
            x=[traj_ax[idx_onset, 0]], y=[traj_ax[idx_onset, 1]], z=[traj_ax[idx_onset, 2]],
            mode='markers',
            marker=dict(size=8, color='black', symbol='diamond'),
            showlegend=False
        ))
        
        title = f"<b>Figure f046: {area} State-Space Trajectory</b><br><sup>N={n_units} units | Var Exp: {np.sum(var)*100:.1f}%</sup>"
        
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(family="Arial", size=18, color="#000000")),
            template="plotly_white",
            scene=dict(
                xaxis_title=f"PC1 ({var[0]*100:.1f}%)",
                yaxis_title=f"PC2 ({var[1]*100:.1f}%)",
                zaxis_title=f"PC3 ({var[2]*100:.1f}%)",
                xaxis=dict(showbackground=True, backgroundcolor="white", gridcolor="#D3D3D3", zerolinecolor="black"),
                yaxis=dict(showbackground=True, backgroundcolor="white", gridcolor="#D3D3D3", zerolinecolor="black"),
                zaxis=dict(showbackground=True, backgroundcolor="white", gridcolor="#D3D3D3", zerolinecolor="black")
            ),
            margin=dict(l=0, r=0, b=0, t=80),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(255,255,255,0.8)", bordercolor="#000000", borderwidth=1
            ),
            modebar_add=['toImage']
        )
        
        html_file = os.path.join(output_dir, f"f046_trajectory_{area}.html")
        fig.write_html(html_file, include_plotlyjs="cdn")
        log.progress(f"Saved interactive 3D HTML figure: {html_file}")
        
        # Explicit User Override: Generate Vectorized SVG
        svg_file = os.path.join(output_dir, f"f046_trajectory_{area}.svg")
        try:
            fig.write_image(svg_file, engine="kaleido")
            log.progress(f"Saved vectorized SVG (Mandate Override): {svg_file}")
        except Exception as e:
            pass