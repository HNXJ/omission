
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from scipy.ndimage import gaussian_filter1d

# Publication-grade plotting standards (Nature/NeurIPS)
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

CONDITION_GROUPS = [['AAAB', 'AXAB', 'AAXB', 'AAAX'], ['BBBA', 'BXBA', 'BBXA', 'BBBX'], ['RRRR', 'RXRR', 'RRXR', 'RRRX']]
GROUP_NAMES = ["A-Base Sequences", "B-Base Sequences", "Random Sequences"]

def smooth_fr(data, sigma=50):
    """Gaussian convolution for smooth firing rate traces."""
    return gaussian_filter1d(data.astype(float), sigma=sigma)

def plot_unit_raster_trace_suite(session, probe_id, local_idx, area_label, filename_tag, array_dir=r'D:\drive\data\arrays', output_dir=r'D:\drive\omission\outputs\oglo-figures'):
    """
    Primate Raster + Trace Suite: Standard visualization for single-unit analysis.
    Generates 6-panel interactive figure with 3 rasters and 3 smoothed PSTH groups.
    """
    array_dir = Path(array_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig = make_subplots(
        rows=6, cols=1, 
        subplot_titles=["RRRR Raster", "RXRR Raster", "RRXR Raster"] + GROUP_NAMES,
        vertical_spacing=0.04, shared_xaxes=True,
        row_heights=[0.08, 0.08, 0.08, 0.24, 0.24, 0.24]
    )
    
    max_fr = 0
    found_any = False

    # 1. Rasters
    for idx, cond in enumerate(['RRRR', 'RXRR', 'RRXR'], start=1):
        try:
            path = array_dir / f"ses{session}-units-probe{probe_id}-spk-{cond}.npy"
            if path.exists():
                data = np.load(path)
                if data.shape[1] > local_idx:
                    unit_spikes = data[:, local_idx, :]
                    trials, times = np.where(unit_spikes > 0)
                    times_ms = times - 1000
                    mask = (times_ms >= -1000) & (times_ms <= 4000)
                    fig.add_trace(go.Scatter(
                        x=times_ms[mask], y=trials[mask], mode='markers',
                        marker=dict(size=2, color='black', symbol='line-ns-open'),
                        showlegend=False
                    ), row=idx, col=1)
                    fig.update_yaxes(title_text="Trials", row=idx, col=1, autorange="reversed")
        except: pass

    # 2. PSTHs
    for group_idx, group in enumerate(CONDITION_GROUPS):
        row_idx = group_idx + 4
        for cond in group:
            p = array_dir / f"ses{session}-units-probe{probe_id}-spk-{cond}.npy"
            if not p.exists(): continue
            try:
                data = np.load(p)
                if data.shape[1] <= local_idx: continue
                fr_trials = data[:, local_idx, :].astype(float) * 1000
                mean_fr = fr_trials.mean(axis=0)
                sem_fr = fr_trials.std(axis=0) / np.sqrt(fr_trials.shape[0])
                
                mean_s = smooth_fr(mean_fr)
                up_s = smooth_fr(mean_fr + sem_fr)
                lo_s = smooth_fr(mean_fr - sem_fr)
                
                time_ms = np.arange(len(mean_s)) - 1000
                mask = (time_ms >= -1000) & (time_ms <= 4000)
                color = COND_COLORS.get(cond, 'gray')
                
                fig.add_trace(go.Scatter(
                    x=np.concatenate([time_ms[mask], time_ms[mask][::-1]]),
                    y=np.concatenate([up_s[mask], lo_s[mask][::-1]]),
                    fill='toself', fillcolor=color, line=dict(color='rgba(0,0,0,0)'),
                    showlegend=False, opacity=0.15
                ), row=row_idx, col=1)
                
                fig.add_trace(go.Scatter(
                    x=time_ms[mask], y=mean_s[mask], mode='lines', name=cond,
                    line=dict(color=color, width=3)
                ), row=row_idx, col=1)
                max_fr = max(max_fr, np.max(up_s[mask]))
                found_any = True
            except: pass

    if not found_any: return

    for r in range(1, 7):
        for ep in EPOCHS:
            fig.add_vrect(x0=ep['start'], x1=ep['end'], fillcolor=ep['color'], opacity=0.08, row=r, col=1)
        for start in [0, 1031, 2062, 3093]:
             fig.add_vline(x=start, line_width=1, line_dash="dash", line_color="black", opacity=0.3, row=r, col=1)

    fig.update_layout(
        title=dict(text=f"Primate Raster + Trace Suite: {filename_tag}<br>{area_label} | Session: {session} | Idx: {local_idx}", font=dict(size=18, family="Arial")),
        xaxis6_title="Time from p1 onset (ms)", template="plotly_white", width=1200, height=1600, showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.03, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(b=150)
    )
    for r in range(4, 7):
        fig.update_yaxes(title_text="FR (Hz)", row=r, col=1, range=[0, max_fr * 1.1])

    out_base = output_dir / f"omission_suite_{filename_tag}"
    fig.write_image(f"{out_base}.png")
    fig.write_html(f"{out_base}.html")
    print(f"Saved: {out_base}.png")
