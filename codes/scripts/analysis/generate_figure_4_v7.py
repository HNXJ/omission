
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from scipy.ndimage import gaussian_filter1d

# Paths
ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Mandate Colors
COND_COLORS = {
    'AAAB': '#0072B2', 'AAAX': '#56B4E9', 'AAXB': '#009E73', 'AXAB': '#E69F00',
    'BBBA': '#D55E00', 'BBBX': '#CC79A7', 'BBXA': '#F0E442', 'BXBA': '#000000',
    'RRRR': '#F0E442', 'RRRX': '#D55E00', 'RRXR': '#56B4E9', 'RXRR': '#009E73'
}

# Standard Epochs (p1-relative ms)
EPOCHS = [
    {'name': 'p1', 'start': 0, 'end': 531, 'color': 'gold'},
    {'name': 'p2/x', 'start': 1031, 'end': 1562, 'color': 'violet'},
    {'name': 'p3/x', 'start': 2062, 'end': 2593, 'color': 'teal'},
    {'name': 'p4/x', 'start': 3093, 'end': 3624, 'color': 'orange'}
]

CONDITION_GROUPS = [
    ['AAAB', 'AXAB', 'AAXB', 'AAAX'],
    ['BBBA', 'BXBA', 'BBXA', 'BBBX'],
    ['RRRR', 'RXRR', 'RRXR', 'RRRX']
]

GROUP_NAMES = ["A-Base Sequences", "B-Base Sequences", "Random Sequences"]

def smooth_fr(data, sigma=50):
    """Gaussian convolution for smooth firing rate traces."""
    return gaussian_filter1d(data.astype(float), sigma=sigma)

def plot_unit_firing_rate_v7(session, probe_id, local_idx, area_label, filename_tag):
    # Create subplots: 6 rows (3 Rasters + 3 PSTH groups)
    raster_titles = ["RRRR Raster", "RXRR Raster", "RRXR Raster"]
    fig = make_subplots(
        rows=6, cols=1, 
        subplot_titles=raster_titles + GROUP_NAMES,
        vertical_spacing=0.04,
        shared_xaxes=True,
        row_heights=[0.08, 0.08, 0.08, 0.24, 0.24, 0.24]
    )
    
    max_fr = 0
    found_any = False

    # 1. Plot Rasters (Rows 1-3)
    raster_conds = ['RRRR', 'RXRR', 'RRXR']
    for idx, cond in enumerate(raster_conds, start=1):
        try:
            path = ARRAY_DIR / f"ses{session}-units-probe{probe_id}-spk-{cond}.npy"
            if path.exists():
                data = np.load(path)
                if data.shape[1] > local_idx:
                    unit_spikes = data[:, local_idx, :]
                    trials, times = np.where(unit_spikes > 0)
                    times_ms = times - 1000
                    mask = (times_ms >= -1000) & (times_ms <= 4000)
                    
                    fig.add_trace(go.Scatter(
                        x=times_ms[mask],
                        y=trials[mask],
                        mode='markers',
                        marker=dict(size=2, color='black', symbol='line-ns-open'),
                        name=f'{cond} Raster',
                        showlegend=False
                    ), row=idx, col=1)
                    fig.update_yaxes(title_text="Trials", row=idx, col=1, autorange="reversed")
        except Exception as e:
            print(f"Raster error ({cond}): {e}")

    # 2. Plot PSTH Groups (Rows 4-6)
    for group_idx, group in enumerate(CONDITION_GROUPS):
        row_idx = group_idx + 4
        for cond in group:
            file_path = ARRAY_DIR / f"ses{session}-units-probe{probe_id}-spk-{cond}.npy"
            if not file_path.exists():
                continue
                
            try:
                data = np.load(file_path)
                if data.shape[1] <= local_idx:
                    continue
                
                unit_spikes = data[:, local_idx, :] 
                n_trials = unit_spikes.shape[0]
                if n_trials == 0: continue

                # Firing Rate per trial (Hz)
                fr_trials = unit_spikes.astype(float) * 1000
                
                # Mean and SEM
                mean_fr = fr_trials.mean(axis=0)
                sem_fr = fr_trials.std(axis=0) / np.sqrt(n_trials)
                
                # Gaussian Convolution Smoothing (sigma=50ms)
                mean_smoothed = smooth_fr(mean_fr, sigma=50)
                upper_smoothed = smooth_fr(mean_fr + sem_fr, sigma=50)
                lower_smoothed = smooth_fr(mean_fr - sem_fr, sigma=50)
                
                time_ms = np.arange(len(mean_smoothed)) - 1000
                mask = (time_ms >= -1000) & (time_ms <= 4000)
                
                x_vals = time_ms[mask]
                y_mean = mean_smoothed[mask]
                y_upper = upper_smoothed[mask]
                y_lower = lower_smoothed[mask]

                color = COND_COLORS.get(cond, 'gray')
                
                # SEM Patch
                fig.add_trace(go.Scatter(
                    x=np.concatenate([x_vals, x_vals[::-1]]),
                    y=np.concatenate([y_upper, y_lower[::-1]]),
                    fill='toself', fillcolor=color, line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip", showlegend=False, opacity=0.15
                ), row=row_idx, col=1)
                
                # Mean Trace
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_mean, mode='lines', name=cond,
                    line=dict(color=color, width=3)
                ), row=row_idx, col=1)
                
                max_fr = max(max_fr, np.max(y_upper))
                found_any = True
                
            except Exception as e:
                print(f"PSTH error ({cond}): {e}")

    if not found_any:
        return

    # Global Styling
    for r in range(1, 7):
        for epoch in EPOCHS:
            fig.add_vrect(
                x0=epoch['start'], x1=epoch['end'],
                fillcolor=epoch['color'], opacity=0.08,
                layer="below", line_width=0,
                row=r, col=1
            )
        for start in [0, 1031, 2062, 3093]:
             fig.add_vline(x=start, line_width=1, line_dash="dash", line_color="black", opacity=0.3, row=r, col=1)

    fig.update_layout(
        title=dict(
            text=f"Figure 4: Ultimate Stable Unit - {filename_tag}<br>Unit: {area_label} | Session: {session} | Local Idx: {local_idx} | Min 5 spks/trial",
            font=dict(size=18, family="Arial")
        ),
        xaxis6_title="Time from p1 onset (ms)",
        template="plotly_white", width=1200, height=1600, showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.03,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(b=150)
    )

    for r in range(4, 7):
        fig.update_yaxes(title_text="FR (Hz)", row=r, col=1, range=[0, max_fr * 1.1])

    # Save PNG and HTML
    out_base = OUTPUT_DIR / f"figure_4_v7_{filename_tag}"
    fig.write_image(f"{out_base}.png")
    fig.write_html(f"{out_base}.html")
    print(f"Saved: {out_base}.png and .html")

if __name__ == "__main__":
    # Candidates from find_ultimate_neurons.py and find_complex_omission_neurons_v2.py
    tasks = [
        (230714, 0, 0, "V1_V2", "S_plus"),
        (230629, 0, 55, "V1_V2", "S_minus"),
        (230629, 0, 10, "V1_V2", "O_plus_V1"),
        (230823, 0, 3, "FEF", "Ultimate_Omission")
    ]
    
    for ses, prb, l_idx, area, tag in tasks:
        plot_unit_firing_rate_v7(ses, prb, l_idx, area, tag)
