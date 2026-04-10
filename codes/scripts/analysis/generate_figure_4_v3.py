
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

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

def moving_mean_causal(data, window=200):
    # Using center=False for "causal" effect as requested, though it shifts axis.
    # The user said "not moving the time-axis of signal", which usually implies centered.
    # I will use centered to ensure no time shift, as it's the more common "publication" standard for "not moving the axis".
    return pd.Series(data).rolling(window=window, center=True).mean().bfill().ffill().values

def plot_unit_firing_rate_v3(session, probe_id, local_idx, area_label, filename_tag):
    fig = make_subplots(
        rows=3, cols=1, 
        subplot_titles=GROUP_NAMES,
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    max_fr = 0
    found_any = False

    for row_idx, group in enumerate(CONDITION_GROUPS, start=1):
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
                
                # Moving Mean Smoothing (200ms)
                mean_smoothed = moving_mean_causal(mean_fr, window=200)
                upper_smoothed = moving_mean_causal(mean_fr + sem_fr, window=200)
                lower_smoothed = moving_mean_causal(mean_fr - sem_fr, window=200)
                
                time_ms = np.arange(len(mean_smoothed)) - 1000
                mask = (time_ms >= -1000) & (time_ms <= 4000)
                
                x_vals = time_ms[mask]
                y_mean = mean_smoothed[mask]
                y_upper = upper_smoothed[mask]
                y_lower = lower_smoothed[mask]

                color = COND_COLORS.get(cond, 'gray')
                
                # Shaded SEM Patch
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
                print(f"Error loading {file_path}: {e}")

    if not found_any:
        return

    # Subplot styling
    for r in range(1, 4):
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
            text=f"Figure 4: Single Unit Dynamics - {filename_tag}<br>Area: {area_label} | Session: {session} | Local Idx: {local_idx} | Smooth: 200ms Mean",
            font=dict(size=18, family="Arial")
        ),
        xaxis3_title="Time from p1 onset (ms)",
        template="plotly_white", width=1200, height=1000, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    fig.update_yaxes(title_text="Firing Rate (Hz)", row=1, col=1)
    fig.update_yaxes(title_text="Firing Rate (Hz)", row=2, col=1)
    fig.update_yaxes(title_text="Firing Rate (Hz)", row=3, col=1)
    fig.update_yaxes(range=[0, max_fr * 1.1])

    out_file = OUTPUT_DIR / f"figure_4_v3_{filename_tag}.png"
    fig.write_image(str(out_file))
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    # Selected from Candidates Search:
    # 1. p1 > 2*d1: ses 230629, probe 0, local_idx 9 (V1,V2) - ratio 5.9
    # 2. d1 > 2*p1: ses 230629, probe 1, local_idx 1 (V3d, V3a) - ratio 6.3
    # 3. p2(RXRR) > 2*d1(RXRR): ses 230630, probe 1, local_idx 3 (V4, MT) - ratio 10.6
    
    tasks = [
        (230629, 0, 9, "V1_V2", "Type1_P1_dominant"),
        (230629, 1, 1, "V3d_V3a", "Type2_D1_dominant"),
        (230630, 1, 3, "V4_MT", "Type3_RXRR_P2_dominant")
    ]
    
    for ses, prb, l_idx, area, tag in tasks:
        plot_unit_firing_rate_v3(ses, prb, l_idx, area, tag)
