import numpy as np
import pandas as pd
import os
import glob
import plotly.graph_objects as go
import json
from pathlib import Path

# Mandated 12 Conditions
CONDITIONS = ['AAAB', 'AAAX', 'AAXB', 'AXAB', 'BBBA', 'BBBX', 'BBXA', 'BXBA', 'RRRR', 'RRRX', 'RRXR', 'RXRR']

# Omission timings (1000ms buffer included)
# P1: 1000-1531, D1: 1531-2031, P2: 2031-2562, D2: 2562-3062, P3: 3062-3593, D3: 3593-4093, P4: 4093-4624
OMISSION_PATCHES = {
    'AXAB': (2031, 2562),
    'BXBA': (2031, 2562),
    'RXRR': (2031, 2562),
    'AAXB': (3062, 3593),
    'BBXA': (3062, 3593),
    'RRXR': (3062, 3593),
    'AAAX': (4093, 4624),
    'BBBX': (4093, 4624),
    'RRRX': (4093, 4624)
}

def generate_fig02():
    bhv_dir = Path(__file__).parents[2] / "data" / "behavioral"
    output_dir = Path(__file__).parents[2] / "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Refining Figure 02: Eye DVA V4...")
    
    for cond_name in CONDITIONS:
        print(f"  - Processing {cond_name}...")
        bhv_paths = glob.glob(os.path.join(bhv_dir, f"ses*-behavioral-{cond_name}.npy"))
        
        all_trials_x = []
        all_trials_y = []
        n_sessions = 0
        
        for path in bhv_paths:
            try:
                # Shape: (n_trials, 4, 6000)
                data = np.load(path)
                data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
                
                # Channel 0: X, Channel 1: Y
                all_trials_x.append(data[:, 0, :])
                all_trials_y.append(data[:, 1, :])
                n_sessions += 1
            except Exception as e:
                print(f"Error loading {path}: {e}")
                
        if not all_trials_x:
            print(f"No data for {cond_name}, skipping.")
            continue
            
        trials_x_arr = np.concatenate(all_trials_x, axis=0)
        trials_y_arr = np.concatenate(all_trials_y, axis=0)
        n_trials = trials_x_arr.shape[0]
        
        mean_x = np.nanmean(trials_x_arr, axis=0)
        sem_x = np.nanstd(trials_x_arr, axis=0) / np.sqrt(n_trials)
        
        mean_y = np.nanmean(trials_y_arr, axis=0)
        sem_y = np.nanstd(trials_y_arr, axis=0) / np.sqrt(n_trials)
        
        time_ax = np.arange(6000)
        
        fig = go.Figure()
        
        # Omission Patch
        if cond_name in OMISSION_PATCHES:
            x0, x1 = OMISSION_PATCHES[cond_name]
            fig.add_vrect(x0=x0, x1=x1, fillcolor="#FF1493", opacity=0.2, layer="below", line_width=0, annotation_text="Omission")

        # Plot X trace with 2-SEM
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_ax, time_ax[::-1]]),
            y=np.concatenate([mean_x + 2*sem_x, (mean_x - 2*sem_x)[::-1]]),
            fill='toself', fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color='rgba(255,255,255,0)'),
            name="X ±2SEM", showlegend=True
        ))
        fig.add_trace(go.Scatter(x=time_ax, y=mean_x, name='Avg X Position', line=dict(color='red', width=2)))

        # Plot Y trace with 2-SEM
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_ax, time_ax[::-1]]),
            y=np.concatenate([mean_y + 2*sem_y, (mean_y - 2*sem_y)[::-1]]),
            fill='toself', fillcolor='rgba(0, 0, 255, 0.2)', line=dict(color='rgba(255,255,255,0)'),
            name="Y ±2SEM", showlegend=True
        ))
        fig.add_trace(go.Scatter(x=time_ax, y=mean_y, name='Avg Y Position', line=dict(color='blue', width=2)))

        fig.update_layout(
            title=f"<b>Fig 02: Eye Trajectories (DVA) - {cond_name}</b><br><sup>N = {n_trials} trials | Sessions: {n_sessions} | Mean ± 2SEM</sup>",
            xaxis_title="Time from Fixation Onset [ms]",
            yaxis_title="Visual Angle [deg]",
            yaxis=dict(range=[-5, 5]), # Fixed DVA range
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        base_filename = os.path.join(output_dir, f"fig_02_eye_dva_{cond_name}")
        fig.write_html(base_filename + ".html")
        fig.write_image(base_filename + ".svg")
        fig.write_image(base_filename + ".png")
        
        # Metadata sidecar
        meta = {
            "script": "generate_fig02_eye_dva.py",
            "condition": cond_name,
            "n_trials": n_trials,
            "n_sessions": n_sessions,
            "window_ms": [0, 6000],
            "omission_patch": OMISSION_PATCHES.get(cond_name, None),
            "channels": {"0": "Eye-X", "1": "Eye-Y"}
        }
        with open(base_filename + ".metadata.json", "w") as f:
            json.dump(meta, f, indent=4)
            
    print(f"Fig 02 Eye DVA V4 completed. Saved to {output_dir}")
