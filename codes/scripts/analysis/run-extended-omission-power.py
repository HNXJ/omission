
from codes.config.paths import BEHAVIORAL_DIR, DATA_DIR, FIGURES_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas as pd
import scipy.io as sio
import os
import glob
import scipy.signal as signal
import scipy.ndimage as ndimage
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 🏺 Madelane Golden Dark Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"
SLATE = "#444444"

# Task Timing (Relative to P1 Onset at Sample 1000)
# Standard Windows
OMISSION_CONFIGS = {
    'p2': {'start': 531, 'end': 2062, 'conds': ['AXAB', 'BXBA', 'RXRR']},
    'p3': {'start': 1562, 'end': 3093, 'conds': ['AAXB', 'BBXA', 'RRXR']},
    'p4': {'start': 2593, 'end': 4124, 'conds': ['AAAX', 'BBBX', 'RRRX']}
}

# Extended Windows (fx-p1-d1-p2-d2-p3-d3 for p2; d1-p2-d2-p3-d3-p4-d4 for p3)
EXTENDED_CONFIGS = {
    'p2_ext': {'start': -500, 'end': 3093, 'conds': ['AXAB', 'BXBA', 'RXRR'], 'label': 'fx-p1-d1-p2-d2-p3-d3'},
    'p3_ext': {'start': 531, 'end': 4124, 'conds': ['AAXB', 'BBXA', 'RRXR'], 'label': 'd1-p2-d2-p3-d3-p4-d4'}
}

EVENT_LINES = {
    'fx': -500, 'p1': 0, 'd1': 531, 'p2': 1031, 'd2': 1562, 
    'p3': 2062, 'd3': 2593, 'p4': 3093, 'd4': 3624
}

# TFR Parameters
FS = 1000.0
W_MS = 100
NPERSEG = int(W_MS * FS / 1000)
NOVERLAP = int(0.98 * NPERSEG)
GAUSS_SIGMA_MS = 20
GAUSS_SIGMA_SAMPLES = GAUSS_SIGMA_MS / (NPERSEG - NOVERLAP)

BANDS = {
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (35, 80)
}

BAND_COLORS = {
    'Theta': 'cyan',
    'Alpha': 'lime',
    'Beta': GOLD,
    'Gamma': VIOLET
}

def smooth_tfr(Sxx, sigma_samples):
    return ndimage.gaussian_filter1d(Sxx, sigma=sigma_samples, axis=-1)

def compute_relative_power(lfp, config):
    """Computes relative dB change for an omission window with SEM."""
    t_start = 1000 + config['start']
    t_end = 1000 + config['end']
    
    # Extract window
    window_data = lfp[:, :, t_start:t_end]
    n_trials, n_ch, n_time = window_data.shape
    
    lfp_probe = np.mean(window_data, axis=1) # Average channels
    
    trial_tfrs = []
    for t in range(n_trials):
        f, t_vec, Sxx = signal.spectrogram(lfp_probe[t], fs=FS, window='hann', 
                                         nperseg=NPERSEG, noverlap=NOVERLAP)
        Sxx_smooth = smooth_tfr(Sxx, GAUSS_SIGMA_SAMPLES)
        trial_tfrs.append(Sxx_smooth)
    
    if not trial_tfrs: return None
    
    trial_tfrs = np.array(trial_tfrs)
    t_ms = (t_vec * 1000) + config['start']
    
    # Baseline for normalization: Use immediate delays surrounding omission
    # For extended plots, we still want the "surprise" normalization.
    # We'll use the same baseline logic as the standard plots.
    if 'p2' in config['conds'][0].lower() or 'ext' in str(config): # Heuristic
        # Usually p2 omission is at 1031. Delay before is 531-1031. Delay after is 1562-2062.
        idx_baseline = np.where(((t_ms > 531) & (t_ms < 1031)) | ((t_ms > 1562) & (t_ms < 2062)))[0]
    else:
        # Default fallback
        idx_baseline = np.arange(min(50, len(t_ms)))

    traces = {}
    for name, (f_min, f_max) in BANDS.items():
        f_idx = np.where((f >= f_min) & (f <= f_max))[0]
        trial_band_power = np.mean(trial_tfrs[:, f_idx, :], axis=1)
        trial_baseline = np.mean(trial_band_power[:, idx_baseline], axis=1, keepdims=True)
        trial_db = 10 * np.log10(trial_band_power / (trial_baseline + 1e-12))
        
        traces[name] = {
            'mean': np.nanmean(trial_db, axis=0),
            'sem': np.nanstd(trial_db, axis=0) / np.sqrt(n_trials),
            'time': t_ms
        }
    return traces

def process_extended_batch():
    data_dir = str(DATA_DIR)
    bhv_dir = str(BEHAVIORAL_DIR / 'omission_bhv/data')
    checkpoint_dir = str(PROCESSED_DATA_DIR)
    output_dir = str(FIGURES_DIR / 'part01')
    os.makedirs(output_dir, exist_ok=True)
    
    mapping_df = pd.read_csv(os.path.join(checkpoint_dir, 'vflip2_mapping_v3.csv'))
    
    bhv_paths = glob.glob(os.path.join(bhv_dir, "*.mat"))
    sessions = sorted(list(set([os.path.basename(p).split('_')[0] for p in bhv_paths])))
    
    print(f"🏺 Found {len(sessions)} sessions for extended analysis: {sessions}")
    
    for sid in sessions:
        print(f"🏺 Extended Batch: Session {sid}")
        lfp_files = glob.glob(os.path.join(data_dir, f'ses{sid}-probe*-lfp-*.npy'))
        
        for f_path in lfp_files:
            fname = os.path.basename(f_path)
            cond = fname.split('-')[-1].replace('.npy', '')
            probe_id = int(fname.split('-')[1].replace('probe', ''))
            
            target_key = None
            if cond in EXTENDED_CONFIGS['p2_ext']['conds']: target_key = 'p2_ext'
            elif cond in EXTENDED_CONFIGS['p3_ext']['conds']: target_key = 'p3_ext'
            
            if not target_key: continue
            
            area_info = mapping_df[(mapping_df['session_id'].astype(str).str.contains(sid)) & 
                                   (mapping_df['probe_id'] == probe_id)]
            if area_info.empty: continue
            area = area_info.iloc[0]['area']
            
            print(f"  - Analyzing Extended LFP: {sid} {area} {cond}")
            try:
                lfp = np.load(f_path, mmap_mode='r')
                traces = compute_relative_power(lfp, EXTENDED_CONFIGS[target_key])
                
                if traces:
                    fig = go.Figure()
                    for name, d in traces.items():
                        t = d['time']
                        mu = d['mean']
                        sem = d['sem']
                        color = BAND_COLORS[name]
                        f_range = BANDS[name]
                        
                        fig.add_trace(go.Scatter(
                            x=np.concatenate([t, t[::-1]]),
                            y=np.concatenate([mu + sem, (mu - sem)[::-1]]),
                            fill='toself', fillcolor=color, opacity=0.2, line=dict(color='rgba(255,255,255,0)'), showlegend=False
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=t, y=mu,
                            name=f"{name} ({f_range[0]}-{f_range[1]}Hz)",
                            line=dict(color=color, width=3)
                        ))
                    
                    for label, t_val in EVENT_LINES.items():
                        fig.add_vline(x=t_val, line_dash="dash", line_color="white", opacity=0.3, annotation_text=label)
                    
                    fig.update_layout(
                        title=f"🏺 Extended Omission Power | {area} ({sid}) | {cond}",
                        xaxis_title="Time (ms)", yaxis_title="Relative Power (dB)",
                        template="plotly_dark", paper_bgcolor=BLACK, plot_bgcolor=BLACK,
                        font=dict(color=GOLD, family="Consolas")
                    )
                    
                    out_name = f"LFP_dB_EXT_{sid}_{area.replace(',', '_').replace(' ', '_')}_P{probe_id}_{cond}.html"
                    fig.write_html(os.path.join(output_dir, out_name))
            except Exception as e:
                print(f"    Error processing Extended LFP {fname}: {e}")


def main(args=None):
    process_extended_batch()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
