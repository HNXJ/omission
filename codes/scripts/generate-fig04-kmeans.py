"""
generate_fig04_kmeans.py
V4 Refinement: K-means clustering of non-P1-responsive units for RRRX.
Group 0 (Gold): Responders (p1 > d1 * 1.1 AND p < 0.05).
Groups 1-4: K-means (k=4) on other units.
Plot d2-p3-d3 and d3-p4-d4 profiles (time-series).
"""
import numpy as np
import pandas as pd
import glob
import os
import json
from scipy.stats import ttest_ind
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Configuration
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data\arrays'
OUTPUT_DIR = Path(__file__).parents[2] / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONDITIONS = ['AAAB', 'AAAX', 'AAXB', 'AXAB', 'BBBA', 'BBBX', 'BBXA', 'BXBA', 'RRRR', 'RRRX', 'RRXR', 'RXRR']

# Windows for profile extraction (ms)
# d2-p3-d3: 2562 - 4093
# d3-p4-d4: 3593 - 5124
WINDOWS = {
    'd2-p3-d3': (2562, 4093),
    'd3-p4-d4': (3593, 5124)
}

EPOCH_WINDOWS = {
    'p1': (1000, 1531), 'd1': (1531, 2031)
}

THEME_COLORS = ['#CFB87C', '#8F00FF', '#00FFCC', '#FF5E00', '#222222'] # Gold (G0), Violet, Teal, Orange, Gray

def smooth_fr(data, window_size=50):
    if len(data) < window_size: return data
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')

def run():
    print("Generating Figure 04: K-means Clustering V4...")
    
    # We focus on RRRX as requested, but loop for completeness if needed.
    # The prompt specifically highlighted RRRX.
    target_cond = 'RRRX'
    
    spike_files = glob.glob(os.path.join(DATA_DIR, f'ses*-units-probe*-spk-{target_cond}.npy'))
    
    unit_fr_traces = [] # List of full 6000ms FR traces
    unit_stats = []     # List of dicts with p1, d1, p_val
    sessions_processed = set()
    
    for f_path in spike_files:
        try:
            ses_id = os.path.basename(f_path).split('-')[0].replace('ses', '')
            spikes = np.load(f_path)
            spikes = np.nan_to_num(spikes, nan=0.0, posinf=0.0, neginf=0.0)
            
            n_trials, n_units, n_samples = spikes.shape
            if n_samples < 6000: continue
            
            sessions_processed.add(ses_id)
            
            # Unit-wise processing
            for u in range(n_units):
                # Calculate trial-averaged FR trace (Hz)
                fr_trace = np.nanmean(spikes[:, u, :], axis=0) * 1000.0
                
                # Significance test P1 vs D1
                p1_trials = np.nanmean(spikes[:, u, 1000:1531], axis=1) * 1000.0
                d1_trials = np.nanmean(spikes[:, u, 1531:2031], axis=1) * 1000.0
                
                p1_mean = np.mean(p1_trials)
                d1_mean = np.mean(d1_trials)
                
                if n_trials > 1:
                    _, p_val = ttest_ind(p1_trials, d1_trials, equal_var=False, nan_policy='omit')
                else:
                    p_val = 1.0
                
                unit_fr_traces.append(fr_trace)
                unit_stats.append({
                    'p1_fr': p1_mean,
                    'd1_fr': d1_mean,
                    'p_val': p_val,
                    'session': ses_id
                })
        except Exception as e:
            print(f"Error reading {f_path}: {e}")

    if not unit_stats:
        print(f"No units found for {target_cond}. Exiting.")
        return

    df = pd.DataFrame(unit_stats)
    traces_arr = np.array(unit_fr_traces) # (n_units, 6000)
    
    # Sanitation
    traces_arr = np.nan_to_num(traces_arr)
    
    # Group 0 (Gold): Responders (p1 > d1 * 1.1 AND p < 0.05)
    is_responder = (df['p1_fr'] > df['d1_fr'] * 1.1) & (df['p_val'] < 0.05)
    df['group'] = -1
    df.loc[is_responder, 'group'] = 0
    
    # Groups 1-4: K-means (k=4) on other units
    rest_idx = df[~is_responder].index
    if len(rest_idx) >= 4:
        # Use full FR trace for clustering (subsampled for speed if needed, but 6000 is okay)
        X = traces_arr[rest_idx, :]
        X_scaled = StandardScaler().fit_transform(X)
        
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        df.loc[rest_idx, 'group'] = clusters + 1 # 1, 2, 3, 4
    elif len(rest_idx) > 0:
        df.loc[rest_idx, 'group'] = 1
        
    # Plotting
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Profile: d2-p3-d3', 'Profile: d3-p4-d4'))
    
    for g in range(5):
        g_idx = df[df['group'] == g].index
        if len(g_idx) == 0: continue
        
        g_traces = traces_arr[g_idx, :]
        mean_g_trace = np.nanmean(g_traces, axis=0)
        sem_g_trace = np.nanstd(g_traces, axis=0) / np.sqrt(len(g_idx))
        
        color = THEME_COLORS[g]
        name = f'Group {g} (N={len(g_idx)})'
        
        # Subplot 1: d2-p3-d3 (2562 - 4093)
        s1, e1 = WINDOWS['d2-p3-d3']
        t1 = np.arange(s1, e1)
        m1 = mean_g_trace[s1:e1]
        err1 = sem_g_trace[s1:e1]
        
        fig.add_trace(go.Scatter(
            x=t1, y=m1, name=name, line=dict(color=color, width=3),
            legendgroup=f'g{g}'
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=np.concatenate([t1, t1[::-1]]),
            y=np.concatenate([m1 + 2*err1, (m1 - 2*err1)[::-1]]),
            fill='toself', fillcolor=color, opacity=0.1, line=dict(color='rgba(255,255,255,0)'),
            showlegend=False, legendgroup=f'g{g}', hoverinfo='skip'
        ), row=1, col=1)
        
        # Subplot 2: d3-p4-d4 (3593 - 5124)
        s2, e2 = WINDOWS['d3-p4-d4']
        t2 = np.arange(s2, e2)
        m2 = mean_g_trace[s2:e2]
        err2 = sem_g_trace[s2:e2]
        
        fig.add_trace(go.Scatter(
            x=t2, y=m2, name=name, line=dict(color=color, width=3),
            legendgroup=f'g{g}', showlegend=False
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=np.concatenate([t2, t2[::-1]]),
            y=np.concatenate([m2 + 2*err2, (m2 - 2*err2)[::-1]]),
            fill='toself', fillcolor=color, opacity=0.1, line=dict(color='rgba(255,255,255,0)'),
            showlegend=False, legendgroup=f'g{g}', hoverinfo='skip'
        ), row=1, col=2)

    # Add pink omission patches
    # P3 Omission is 3062-3593
    fig.add_vrect(x0=3062, x1=3593, fillcolor="#FF1493", opacity=0.2, layer="below", line_width=0, row=1, col=1)
    fig.add_vrect(x0=3062, x1=3593, fillcolor="#FF1493", opacity=0.2, layer="below", line_width=0, row=1, col=2)

    fig.update_layout(
        title=f"<b>Fig 04: K-means Responsive Clusters ({target_cond})</b><br><sup>N = {len(df)} total units | Group 0 = P1 Responders</sup>",
        template="plotly_white",
        xaxis_title="Time [ms]",
        yaxis_title="Firing Rate [Hz]",
        xaxis2_title="Time [ms]"
    )
    
    base_filename = os.path.join(OUTPUT_DIR, f"fig_04_kmeans_{target_cond}")
    fig.write_html(base_filename + ".html")
    fig.write_image(base_filename + ".svg")
    fig.write_image(base_filename + ".png")
    
    # Metadata sidecar
    meta = {
        "script": "generate_fig04_kmeans.py",
        "condition": target_cond,
        "total_units": len(df),
        "group_counts": df['group'].value_counts().to_dict(),
        "sessions": list(sessions_processed),
        "windows": WINDOWS,
        "colors": {f"Group {i}": THEME_COLORS[i] for i in range(5)}
    }
    with open(base_filename + ".metadata.json", "w") as f:
        json.dump(meta, f, indent=4)
        
    print(f"Fig 04 K-means V4 completed for {target_cond}. Saved to {OUTPUT_DIR}")

if __name__ == '__main__':
    run()
