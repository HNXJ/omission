
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

def plot_unit_firing_rate_v4(session, probe_id, local_idx, area_label, filename_tag):
    # Create subplots: 4 rows (Raster + 3 PSTH groups)
    fig = make_subplots(
        rows=4, cols=1, 
        subplot_titles=["RRRR Trial Raster"] + GROUP_NAMES,
        vertical_spacing=0.06,
        shared_xaxes=True,
        row_heights=[0.2, 0.26, 0.26, 0.26]
    )
    
    max_fr = 0
    found_any = False

    # 1. Plot Raster for RRRR (Top Plot)
    try:
        rrrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe_id}-spk-RRRR.npy"
        if rrrr_path.exists():
            rrrr_data = np.load(rrrr_path)
            if rrrr_data.shape[1] > local_idx:
                unit_spikes = rrrr_data[:, local_idx, :] # (trials, time)
                n_trials = unit_spikes.shape[0]
                
                # Find spike coordinates
                trials, times = np.where(unit_spikes > 0)
                times_ms = times - 1000 # p1-relative
                
                # Filter to window
                mask = (times_ms >= -1000) & (times_ms <= 4000)
                
                fig.add_trace(go.Scatter(
                    x=times_ms[mask],
                    y=trials[mask],
                    mode='markers',
                    marker=dict(size=2, color='black', symbol='line-ns-open'),
                    name='RRRR Raster',
                    showlegend=False
                ), row=1, col=1)
                fig.update_yaxes(title_text="Trials", row=1, col=1, autorange="reversed")
    except Exception as e:
        print(f"Raster error: {e}")

    # 2. Plot PSTH Groups
    for group_idx, group in enumerate(CONDITION_GROUPS):
        row_idx = group_idx + 2
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

                fr_trials = unit_spikes.astype(float) * 1000
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
    for r in range(1, 5):
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
            text=f"Figure 4: Single Unit Dynamics & RRRR Raster<br>Unit: {area_label} | Session: {session} | Local Idx: {local_idx} | Smooth: Gaussian Convolved (sigma=50ms)",
            font=dict(size=18, family="Arial")
        ),
        xaxis4_title="Time from p1 onset (ms)",
        template="plotly_white", width=1200, height=1300, showlegend=True,
        # Move legend to bottom and center it to avoid overlap
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(b=150) # Increase bottom margin for legend
    )

    for r in range(2, 5):
        fig.update_yaxes(title_text="FR (Hz)", row=r, col=1, range=[0, max_fr * 1.1])

    # Save PNG and HTML
    out_base = OUTPUT_DIR / f"figure_4_v4_{filename_tag}"
    fig.write_image(f"{out_base}.png")
    fig.write_html(f"{out_base}.html")
    print(f"Saved: {out_base}.png and .html")

if __name__ == "__main__":
    # Candidates from find_specific_neurons_v2.py (PR >= 0.99, SNR > 1.0)
    tasks = [
        (230629, 0, 9, "V1_V2", "Type1_P1_dominant"),
        (230629, 1, 1, "V3d_V3a", "Type2_D1_dominant"),
        (230630, 1, 3, "V4_MT", "Type3_RXRR_P2_dominant")
    ]
    
    for ses, prb, l_idx, area, tag in tasks:
        plot_unit_firing_rate_v4(ses, prb, l_idx, area, tag)
