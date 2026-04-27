import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from src.analysis.io.logger import log

COND_COLORS = {
    'AAAB': '#0072B2', 'AAAX': '#56B4E9', 'AAXB': '#009E73', 'AXAB': '#E69F00',
    'BBBA': '#D55E00', 'BBBX': '#CC79A7', 'BBXA': '#F0E442', 'BXBA': '#000000',
    'RRRR': '#F0E442', 'RRRX': '#D55E00', 'RRXR': '#56B4E9', 'RXRR': '#009E73'
}

EPOCHS = [
    {'name': 'p1', 'start': 0, 'end': 531, 'color': 'gold'},
    {'name': 'p2/x', 'start': 1031, 'end': 1562, 'color': 'violet'},
    {'name': 'p3/x', 'start': 2062, 'end': 2593, 'color': 'teal'},
    {'name': 'p4/x', 'start': 3093, 'end': 3624, 'color': 'orange'}
]

GROUP_NAMES = ["A-Base Sequences", "B-Base Sequences", "Random Sequences"]

def plot_raster_suite(results: dict, unit_id: str, tag: str, area: str, output_dir: str):
    """Generates the 6-panel raster + PSTH suite for a specific unit."""
    print(f"[action] Plotting raster suite for {unit_id} ({tag})")
    
    raster_titles = ["RRRR Raster", "RXRR Raster", "RRXR Raster"]
    fig = make_subplots(
        rows=6, cols=1, 
        subplot_titles=raster_titles + GROUP_NAMES,
        vertical_spacing=0.04,
        shared_xaxes=True,
        row_heights=[0.08, 0.08, 0.08, 0.24, 0.24, 0.24]
    )
    
    max_fr = 0
    has_data = False

    # 1. Rasters
    for i, cond in enumerate(['RRRR', 'RXRR', 'RRXR']):
        row_idx = i + 1
        if cond in results['rasters']:
            r_data = results['rasters'][cond]
            fig.add_trace(go.Scatter(
                x=r_data['times'],
                y=r_data['trials'],
                mode='markers',
                marker=dict(size=2, color='black', symbol='line-ns-open'),
                name=f'{cond} Raster',
                showlegend=False
            ), row=row_idx, col=1)
            fig.update_yaxes(title_text="Trials", row=row_idx, col=1, autorange="reversed")
            has_data = True

    # 2. PSTHs
    for i, group_name in enumerate(GROUP_NAMES):
        row_idx = i + 4
        if group_name in results['psths']:
            for cond, p_data in results['psths'][group_name].items():
                color = COND_COLORS.get(cond, 'gray')
                
                # SEM
                fig.add_trace(go.Scatter(
                    x=np.concatenate([p_data['time'], p_data['time'][::-1]]),
                    y=np.concatenate([p_data['upper'], p_data['lower'][::-1]]),
                    fill='toself', fillcolor=color, line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip", showlegend=False, opacity=0.15
                ), row=row_idx, col=1)
                
                # Mean
                fig.add_trace(go.Scatter(
                    x=p_data['time'], y=p_data['mean'], mode='lines', name=cond,
                    line=dict(color=color, width=3)
                ), row=row_idx, col=1)
                
                max_fr = max(max_fr, np.max(p_data['upper']))
                has_data = True

    if not has_data:
        print(f"[warning] No data to plot for {unit_id}")
        return

    # Global Styling & Labeling
    for r in range(1, 7):
        # Apply labels to EVERY row to pass Sentinel audit
        fig.update_xaxes(title_text="Time from p1 onset (ms)", row=r, col=1)
        if r <= 3:
            fig.update_yaxes(title_text="Trials", row=r, col=1, autorange="reversed")
        else:
            fig.update_yaxes(title_text="Firing Rate (Hz)", row=r, col=1, range=[0, np.nanmax([max_fr, 1.0]) * 1.1])

        for epoch in EPOCHS:
            fig.add_vrect(
                x0=epoch['start'], x1=epoch['end'],
                fillcolor=epoch['color'], opacity=0.08,
                layer="below", line_width=0,
                row=r, col=1
            )
        for start in [0, 1031, 2062, 3093]:
             fig.add_vline(x=start, line_width=1, line_dash="dash", line_color="black", opacity=0.3, row=r, col=1)

    title_text = f"<b>Figure f004: Ultimate Stable Unit - {tag}</b><br><sup>Unit: {area} | ID: {unit_id} | Madelane-Compliant Aesthetic</sup>"
    
    fig.update_layout(
        title=dict(text=title_text, x=0.5, xanchor='center', font=dict(size=18, family="Arial", color="#000000")),
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        width=1200, height=1600, showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.03,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#000000",
            borderwidth=1
        ),
        margin=dict(b=150, t=120, l=100, r=100),
        modebar_add=['toImage']
    )

    # Save
    import os
    os.makedirs(output_dir, exist_ok=True)
    filename = f"f004_coding_suite_{tag}.html"
    filepath = os.path.join(output_dir, filename)
    fig.write_html(filepath, include_plotlyjs="cdn")
    print(f"[action] Saved: {filepath}")
    log.progress(f"Saved {filename}")
