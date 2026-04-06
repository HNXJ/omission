from codes.config.paths import DATA_DIR, FIGURES_DIR

import numpy as np
import os
import plotly.graph_objects as go
import plotly.io as pio

# Madelane Golden Dark + Violet Theme
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
SLATE = '#708090'
WHITE = '#FFFFFF'

def get_polar_direction(eye_x, eye_y, thresh=0.005):
    """Calculates polar direction for significant movements."""
    dx = np.diff(eye_x)
    dy = np.diff(eye_y)
    mag = np.sqrt(dx**2 + dy**2)
    valid = mag > thresh
    angles = np.arctan2(dy[valid], dx[valid])
    return np.degrees(angles) % 360

def plot_rose_directions_grid_plotly(directions_grid, session_id):
    """Plots Rose Plots in a 3x4 grid (Conditions x Presentations)."""
    from plotly.subplots import make_subplots
    
    # Grid: 3 rows (AAAB, BBBA, RRRR), 4 columns (P1, P2, P3, P4)
    conds = ['AAAB', 'BBBA', 'RRRR']
    ps = ['P1', 'P2', 'P3', 'P4']
    
    fig = make_subplots(
        rows=3, cols=4, 
        specs=[[{'type': 'polar'}]*4]*3,
        subplot_titles=[f"{c} - {p}" for c in conds for p in ps],
        vertical_spacing=0.05,
        horizontal_spacing=0.02
    )
    
    for r, ctx in enumerate(conds):
        for c, p_idx in enumerate(range(4)):
            dirs = directions_grid.get(ctx, {}).get(p_idx, [])
            
            if len(dirs) > 0:
                counts, bins = np.histogram(dirs, bins=36, range=(0, 360))
                
                # Determine color: GOLD for A, VIOLET for B, SLATE for R
                color = GOLD if 'A' in ctx else (VIOLET if 'B' in ctx else SLATE)
                
                fig.add_trace(go.Barpolar(
                    r=counts,
                    theta=bins[:-1],
                    width=[10]*36,
                    marker_color=color,
                    marker_line_color=WHITE,
                    marker_line_width=0.5,
                    opacity=0.8,
                    name=f"{ctx}_{ps[c]}"
                ), row=r+1, col=c+1)
    
    fig.update_layout(
        template='plotly_dark',
        title=f"Eye Movement Directionality (3x4 Grid): Session {session_id}",
        paper_bgcolor=BLACK,
        plot_bgcolor=BLACK,
        font_color=WHITE,
        height=1000,
        showlegend=False
    )
    
    # Clean up polar axes
    fig.update_polars(radialaxis_showticklabels=False, angularaxis_showticklabels=False)
    
    html_path = os.path.join(str(FIGURES_DIR), f"FIG_Eye_Rose_Grid_{session_id}.html")
    svg_path = os.path.join(str(FIGURES_DIR), f"FIG_Eye_Rose_Grid_{session_id}.svg")
    
    fig.write_html(html_path)
    fig.write_image(svg_path)
    print(f"Saved Rose Grid: {html_path}, {svg_path}")

def plot_temporal_trajectories_plotly(session_results, session_id):
    """Plots temporal trajectories using Plotly with extreme scaling."""
    from plotly.subplots import make_subplots
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        subplot_titles=('Eye-X (Z-score)', 'Eye-Y (Z-score)'))
    
    time_ms = np.arange(6000) - 1000
    contexts = ['AAAB', 'BBBA']
    colors = [GOLD, VIOLET]
    
    all_vals_x = []
    all_vals_y = []
    
    for ctx, color in zip(contexts, colors):
        if ctx not in session_results: continue
        
        mx = np.mean(session_results[ctx]['eye_x'], axis=0)
        sx = np.std(session_results[ctx]['eye_x'], axis=0) / np.sqrt(session_results[ctx]['eye_x'].shape[0])
        my = np.mean(session_results[ctx]['eye_y'], axis=0)
        sy = np.std(session_results[ctx]['eye_y'], axis=0) / np.sqrt(session_results[ctx]['eye_y'].shape[0])
        
        # X-Trace
        fig.add_trace(go.Scatter(x=time_ms, y=mx, line=dict(color=color), name=f'{ctx} X'), row=1, col=1)
        fig.add_trace(go.Scatter(x=time_ms, y=mx+sx, line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=time_ms, y=mx-sx, fill='tonexty', line=dict(width=0), 
                                 fillcolor=f"rgba{tuple(list(int(color[1:][i:i+2], 16) for i in (0, 2, 4)) + [0.2])}", 
                                 showlegend=False), row=1, col=1)
        
        # Y-Trace
        fig.add_trace(go.Scatter(x=time_ms, y=my, line=dict(color=color), name=f'{ctx} Y'), row=2, col=1)
        fig.add_trace(go.Scatter(x=time_ms, y=my+sy, line=dict(width=0), showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=time_ms, y=my-sy, fill='tonexty', line=dict(width=0), 
                                 fillcolor=f"rgba{tuple(list(int(color[1:][i:i+2], 16) for i in (0, 2, 4)) + [0.2])}", 
                                 showlegend=False), row=2, col=1)
        
        all_vals_x.extend([np.min(mx-sx), np.max(mx+sx)])
        all_vals_y.extend([np.min(my-sy), np.max(my+sy)])

    # Event Lines
    for row in [1, 2]:
        fig.add_vline(x=0, line_dash="dash", line_color=WHITE, row=row, col=1)
        for i in range(1, 5):
            fig.add_vline(x=i*531, line_dash="dot", line_color=SLATE, opacity=0.5, row=row, col=1)

    fig.update_yaxes(range=[min(all_vals_x)*1.1, max(all_vals_x)*1.1], row=1, col=1)
    fig.update_yaxes(range=[min(all_vals_y)*1.1, max(all_vals_y)*1.1], row=2, col=1)
    
    fig.update_layout(template='plotly_dark', title=f'Temporal Eye Trajectories: {session_id}',
                      paper_bgcolor=BLACK, plot_bgcolor=BLACK, height=800)
    
    html_path = os.path.join(str(FIGURES_DIR), f"FIG_Eye_Temporal_Trajectories_{session_id}.html")
    svg_path = os.path.join(str(FIGURES_DIR), f"FIG_Eye_Temporal_Trajectories_{session_id}.svg")
    
    fig.write_html(html_path)
    fig.write_image(svg_path)
    print(f"Saved Trajectories: {html_path}, {svg_path}")

def run_eye_consolidated_plotly(data_dir, session_id):
    from run_behavioral_decoding_suite import analyze_session_eye
    results = analyze_session_eye(data_dir, session_id)
    
    # Presentations: P1: 1000-1531, P2: 2031-2562, P3: 3062-3593, P4: 4093-4624
    p_windows = [(1000, 1531), (2031, 2562), (3062, 3593), (4093, 4624)]
    
    grid_data = {}
    for ctx in ['AAAB', 'BBBA', 'RRRR']:
        if ctx in results:
            grid_data[ctx] = {}
            ex = results[ctx]['eye_x']
            ey = results[ctx]['eye_y']
            
            for p_idx, (start, end) in enumerate(p_windows):
                # Calculate directions for this window specifically
                dirs = get_polar_direction(ex[:, start:end].flatten(), ey[:, start:end].flatten())
                grid_data[ctx][p_idx] = dirs
                
    if grid_data: plot_rose_directions_grid_plotly(grid_data, session_id)
    
    # Temporal
    plot_temporal_trajectories_plotly(results, session_id)


def main(args=None):
    run_eye_consolidated_plotly(str(DATA_DIR), "230629")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
