"""
lfp_plotting_utils.py: Utility functions for LFP plotting.
"""
import plotly.graph_objects as go

def add_mean_sem_trace(fig, x, y, sem, row, col, color, name):
    """
    Adds a mean trace with SEM shading to a subplot.
    """
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        line=dict(color=color),
        name=name
    ), row=row, col=col)
    
    fig.add_trace(go.Scatter(
        x=x.tolist() + x.tolist()[::-1],
        y=(y + sem).tolist() + (y - sem).tolist()[::-1],
        fill='toself',
        fillcolor=color,
        opacity=0.2,
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        name=f"{name} SEM"
    ), row=row, col=col)

def set_global_layout(fig, title):
    """
    Applies a global layout to the figure.
    """
    fig.update_layout(
        title_text=title,
        template="plotly_white",
        font=dict(family="Arial")
    )
