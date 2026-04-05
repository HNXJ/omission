"""
generate_fig07_lfp_spk_corr.py
OMISSION 2026: 22-Cluster Correlation (LFP-SPK) - V4 Refined
Pearson r between spikes and LFP power (2-150Hz, 2Hz steps).
2 clusters per area (11 areas * 2 = 22 traces).
Window: fx (0ms) to d4 (5124ms).
Theme: plotly_white, Triple Export.
"""
import os
import glob
import h5py
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
from pathlib import Path
from scipy.signal import welch
from scipy.stats import pearsonr
from sklearn.cluster import KMeans

# Configuration
DATA_DIR = Path(__file__).parents[2] / "data" / "arrays"
OUTPUT_DIR = Path(__file__).parents[2] / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FS = 1000.0
TARGET_FREQS = np.arange(2, 152, 2) # 2 to 150 inclusive
CONDITIONS = ['AAAB', 'AAAX', 'AAXB', 'AXAB', 'BBBA', 'BBBX', 'BBXA', 'BXBA', 'RRRR', 'RRRX', 'RRXR', 'RXRR']

# Time Window: fx to d4 (ms)
WIN_START = 0
WIN_END = 5124

CANONICAL_AREAS = ['V1', 'V2', 'V3', 'V4', 'MT', 'MST', 'TEO', 'FST', 'DP', 'PFC', 'FEF']

SESSION_AREAS = {
    '230831': {'0': 'FEF', '1': 'MT', '2': 'V4'},
    '230901': {'0': 'PFC', '1': 'MT', '2': 'V4'},
    '230720': {'0': 'V1', '1': 'V4'},
    '230629': {'0': 'V1', '1': 'V3'},
    '230630': {'0': 'PFC', '1': 'V4', '2': 'V3'},
    '230714': {'0': 'V1', '1': 'V3'},
    '230719': {'0': 'V1', '1': 'DP', '2': 'V3'},
    '230721': {'0': 'V1', '1': 'V3'},
    '230816': {'0': 'PFC', '1': 'V4', '2': 'V3'},
    '230818': {'0': 'PFC', '1': 'TEO', '2': 'MT'},
    '230823': {'0': 'FEF', '1': 'MT', '2': 'V1'},
    '230825': {'0': 'PFC', '1': 'MT', '2': 'V4'},
    '230830': {'0': 'PFC', '1': 'V4', '2': 'V1'}
}

def simplify_area(name):
    name = name.upper().replace(' ', '')
    for area in CANONICAL_AREAS:
        if area in name: return area
    return 'Other'

def get_lfp_power_trials(session_id, area_key, condition):
    """Computes trial-by-trial LFP power for each target frequency."""
    h5_path = os.path.join(DATA_DIR, f'lfp_by_area_ses-{session_id}.h5')
    if not os.path.exists(h5_path): return None
    try:
        with h5py.File(h5_path, 'r') as f:
            matched_key = None
            for k in f.keys():
                if k.replace(' ', '') == area_key.replace(' ', ''):
                    matched_key = k
                    break
            
            if matched_key and condition in f[matched_key]:
                # data: (n_trials, n_channels, 6000)
                # Take window
                data = f[matched_key][condition][:, :, WIN_START:WIN_END]
                data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
                
                # Welch power per trial (averaged across channels)
                # Average channels first to reduce noise
                sig = np.nanmean(data, axis=1) # (n_trials, time)
                nperseg = min(1000, sig.shape[1])
                f_welch, pxx = welch(sig, fs=FS, nperseg=nperseg, axis=1)
                
                # Interpolate to target frequencies
                interp_pow = np.zeros((sig.shape[0], len(TARGET_FREQS)))
                for i in range(sig.shape[0]):
                    interp_pow[i, :] = np.interp(TARGET_FREQS, f_welch, pxx[i, :])
                return interp_pow
    except Exception as e:
        print(f"LFP Load Error ({session_id}, {area_key}): {e}")
        return None
    return None

def get_unit_spikes_trials(session_id, probe_id, condition):
    """Computes trial-by-trial spike counts for each unit."""
    f_path = os.path.join(DATA_DIR, f'ses{session_id}-units-probe{probe_id}-spk-{condition}.npy')
    if not os.path.exists(f_path): return None
    try:
        spikes = np.load(f_path)
        spikes = np.nan_to_num(spikes, nan=0.0, posinf=0.0, neginf=0.0)
        # spikes: (n_trials, n_units, 6000)
        # Take window and sum
        win_spk = spikes[:, :, WIN_START:WIN_END]
        counts = np.sum(win_spk, axis=2) # (n_trials, n_units)
        return counts
    except Exception as e:
        print(f"Spike Load Error ({session_id}, Probe {probe_id}): {e}")
        return None

def run():
    print("Generating Figure 07: LFP-SPK Correlation V4...")
    
    for cond in CONDITIONS:
        print(f"  - Processing {cond}...")
        area_agg_r = {area: {0: [], 1: []} for area in CANONICAL_AREAS}
        total_units_global = 0
        sessions_processed = set()
        
        for ses, probe_map in SESSION_AREAS.items():
            for pid, area_key in probe_map.items():
                lfp_pow = get_lfp_power_trials(ses, area_key, cond)
                spk_counts = get_unit_spikes_trials(ses, pid, cond)
                
                if lfp_pow is None or spk_counts is None: continue
                if lfp_pow.shape[0] != spk_counts.shape[0]: continue
                
                n_trials, n_units = spk_counts.shape
                if n_trials < 10 or n_units < 2: continue
                
                simp = simplify_area(area_key)
                if simp not in CANONICAL_AREAS: continue
                
                sessions_processed.add(ses)
                total_units_global += n_units
                
                # Cluster units in this session/probe into 2 groups
                # Standardize spike counts across trials for each unit
                spk_norm = (spk_counts - np.mean(spk_counts, axis=0)) / (np.std(spk_counts, axis=0) + 1e-12)
                spk_norm = np.nan_to_num(spk_norm)
                
                try:
                    kmeans = KMeans(n_clusters=2, random_state=42, n_init=5)
                    clusters = kmeans.fit_predict(spk_norm.T) # Cluster units (transpose to cluster by features/trials)
                    
                    for c_id in [0, 1]:
                        u_idx = np.where(clusters == c_id)[0]
                        if len(u_idx) == 0: continue
                        
                        # Mean spike count of the cluster across trials
                        cluster_spk_trials = np.mean(spk_counts[:, u_idx], axis=1)
                        
                        # Correlate cluster spikes with LFP power at each frequency
                        r_spectrum = np.zeros(len(TARGET_FREQS))
                        for f_idx in range(len(TARGET_FREQS)):
                            f_pow_trials = lfp_pow[:, f_idx]
                            if np.std(cluster_spk_trials) > 0 and np.std(f_pow_trials) > 0:
                                r, _ = pearsonr(cluster_spk_trials, f_pow_trials)
                                r_spectrum[f_idx] = np.nan_to_num(r)
                        
                        area_agg_r[simp][c_id].append(r_spectrum)
                except: continue

        # Plotting
        fig = go.Figure()
        colors = pc.qualitative.Alphabet
        
        traces_added = 0
        for i, area in enumerate(CANONICAL_AREAS):
            color = colors[i % len(colors)]
            for c_id in [0, 1]:
                r_spectra = area_agg_r[area][c_id]
                if not r_spectra: continue
                
                r_mat = np.array(r_spectra)
                mean_r = np.nanmean(r_mat, axis=0)
                sem_r = np.nanstd(r_mat, axis=0) / np.sqrt(len(r_spectra))
                
                dash = 'solid' if c_id == 0 else 'dot'
                name = f"{area} Cluster {c_id}"
                
                # Shading
                fig.add_trace(go.Scatter(
                    x=np.concatenate([TARGET_FREQS, TARGET_FREQS[::-1]]),
                    y=np.concatenate([mean_r + 2*sem_r, (mean_r - 2*sem_r)[::-1]]),
                    fill='toself',
                    fillcolor=f"rgba{tuple(list(pc.hex_to_rgb(color)) + [0.15])}",
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=False, hoverinfo='skip'
                ))
                
                # Mean Line
                fig.add_trace(go.Scatter(
                    x=TARGET_FREQS, y=mean_r,
                    mode='lines',
                    line=dict(color=color, dash=dash, width=2.5),
                    name=name
                ))
                traces_added += 1

        fig.update_layout(
            title=f"<b>Fig 07: LFP-Spike Correlation ({cond})</b><br><sup>Pearson's r (trial-by-trial) | 2 clusters per area | Window: fx-d4</sup>",
            xaxis_title="Frequency [Hz]",
            yaxis_title="Correlation [Pearson's r]",
            template="plotly_white",
            legend=dict(font=dict(size=10)),
            yaxis=dict(range=[-0.4, 0.4])
        )
        
        base_name = os.path.join(OUTPUT_DIR, f"fig_07_lfp_spk_corr_{cond}")
        fig.write_html(base_name + ".html")
        fig.write_image(base_name + ".svg")
        fig.write_image(base_name + ".png")
        
        # Metadata
        meta = {
            "condition": cond,
            "total_units": total_units_global,
            "n_sessions": len(sessions_processed),
            "window": [WIN_START, WIN_END],
            "n_traces": traces_added
        }
        with open(base_name + ".metadata.json", "w") as fm:
            json.dump(meta, fm, indent=4)
            
    print(f"Fig 07 LFP-SPK Corr V4 completed.")

if __name__ == '__main__':
    run()
