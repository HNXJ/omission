"""
Figure 4: Single-neuron examples (PSTH + Rasters)
Motivation: 
- Omission as the ultimate error signal (no sensory-motor confound).
- Characterizing S+, S-, O+, O- profiles in NHPs.
- Linking to neurobiology of schizophrenia (deficit in omission coding).

Layout:
- 5 Rows: [S+, S-, S-(add), O+, O-]
- Column 1: PSTH (RRRR, RXRR, RRXR, RRRX)
- Column 2: Raster Plot (Trials grouped by condition)
"""

import os
import sys
import numpy as np
import pandas as pd
import plotly.subplots as sp
import plotly.graph_objects as go
from pathlib import Path
from scipy.ndimage import gaussian_filter1d

# Add omission repo to path
sys.path.append(r'D:\drive\omission')

# Paths
ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-4')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
CONDITIONS = ['RRRR', 'RXRR', 'RRXR', 'RRRX']
COLORS = {'RRRR': 'red', 'RXRR': 'blue', 'RRXR': 'green', 'RRRX': 'orange'}
FS = 1000.0  # Sampling rate

# Selected Units (session, probe, unit_idx, label)
UNITS = [
    (230720, 0, 105, "S+ Example"),
    (230901, 2, 35,  "S- Example 1"),
    (230630, 1, 106, "S- Example 2"),
    (230830, 0, 107, "O+ Example"),
    (230831, 2, 27,  "O- Example")
]

def load_unit_data(session, probe, unit_idx):
    """Loads all conditions for a single unit."""
    data = {}
    for cond in CONDITIONS:
        path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-{cond}.npy"
        if path.exists():
            arr = np.load(path) # (trials, units, time)
            if unit_idx < arr.shape[1]:
                data[cond] = arr[:, unit_idx, :] # (trials, time)
    return data

def main():
    print("Generating Figure 4: Single-neuron examples...")
    
    fig = sp.make_subplots(
        rows=5, cols=2,
        column_widths=[0.6, 0.4],
        subplot_titles=[f"<b>{u[3]}</b> (PSTH)" if i%2==0 else "Raster" for i, u in enumerate(UNITS*2)],
        horizontal_spacing=0.1,
        vertical_spacing=0.06
    )

    time_ms = np.arange(-1000, 4000) # 0 to 5000 indices

    for row_idx, (session, probe, u_idx, label) in enumerate(UNITS, 1):
        print(f" Processing Row {row_idx}: {label} (Ses{session}, P{probe}, U{u_idx})")
        unit_data = load_unit_data(session, probe, u_idx)
        
        # --- Column 1: PSTH ---
        for cond in CONDITIONS:
            if cond not in unit_data: continue
            
            trials = unit_data[cond] # (N, 6000)
            mean_spk = trials.mean(axis=0) # (6000,)
            fr = mean_spk * FS
            fr_smoothed = gaussian_filter1d(fr, sigma=40)
            
            # Crop to -1000 to 4000 (indices 0 to 5000)
            trace = fr_smoothed[0:5000]
            
            fig.add_trace(go.Scatter(
                x=time_ms, y=trace,
                line=dict(color=COLORS[cond], width=2),
                name=cond, showlegend=(row_idx == 1),
                legendgroup=cond
            ), row=row_idx, col=1)

        # --- Column 2: Raster ---
        current_trial_offset = 0
        for cond in CONDITIONS:
            if cond not in unit_data: continue
            
            trials = unit_data[cond][:, 0:5000] # (N, 5000)
            n_trials = trials.shape[0]
            
            # Find spike indices (where value == 1)
            trial_indices, time_indices = np.where(trials > 0)
            
            # Adjust time to ms and trials to offset
            spike_times = time_ms[time_indices]
            spike_trials = trial_indices + current_trial_offset
            
            fig.add_trace(go.Scatter(
                x=spike_times, y=spike_trials,
                mode='markers',
                marker=dict(size=2, color=COLORS[cond], symbol='line-ns-open'),
                showlegend=False, hoverinfo='skip'
            ), row=row_idx, col=2)
            
            current_trial_offset += n_trials

        # Add vertical timing lines
        for v_time in [0, 1031, 2062, 3093]:
            fig.add_vline(x=v_time, line_width=1, line_dash="dash", line_color="gray", opacity=0.3, row=row_idx, col=1)
            fig.add_vline(x=v_time, line_width=1, line_dash="dash", line_color="gray", opacity=0.3, row=row_idx, col=2)

        fig.update_yaxes(title_text="Hz", row=row_idx, col=1)
        fig.update_yaxes(title_text="Trials", row=row_idx, col=2)

    fig.update_xaxes(title_text="Time from P1 (ms)", row=5, col=1)
    fig.update_xaxes(title_text="Time from P1 (ms)", row=5, col=2)

    fig.update_layout(
        title_text="Figure 4: Representative Single-Neuron Examples and Rasters",
        template="plotly_white",
        height=1400, width=1000,
        font=dict(color="black")
    )

    print("Saving outputs...")
    fig.write_html(OUTPUT_DIR / 'figure-4.html')
    fig.write_image(OUTPUT_DIR / 'figure-4.svg')
    fig.write_image(OUTPUT_DIR / 'figure-4.png', scale=2)
    
    # Save selected unit metadata
    selected_meta = []
    for u in UNITS:
        selected_meta.append({
            'session': u[0],
            'probe': u[1],
            'unit_idx': u[2],
            'label': u[3]
        })
    pd.DataFrame(selected_meta).to_csv(OUTPUT_DIR / 'figure4_selected_units.csv', index=False)
    
    print(f"Done. Outputs in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
