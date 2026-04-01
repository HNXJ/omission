
import numpy as np
import pandas as pd
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
# d(k-1) -> p(k) -> d(k)
# Total ~1531ms
OMISSION_CONFIGS = {
    'p2': {'start': 531, 'end': 2062, 'label': 'AXAB/BXBA/RXRR'},
    'p3': {'start': 1562, 'end': 3093, 'label': 'AAXB/BBXA/RRXR'},
    'p4': {'start': 2593, 'end': 4124, 'label': 'AAAX/BBBX/RRRX'}
}

# TFR Parameters
FS = 1000.0
W_MS = 100
NPERSEG = int(W_MS * FS / 1000)
NOVERLAP = int(0.98 * NPERSEG)
GAUSS_SIGMA_MS = 20
GAUSS_SIGMA_SAMPLES = GAUSS_SIGMA_MS / (NPERSEG - NOVERLAP) # Rough approximation

def smooth_tfr(Sxx, sigma_samples):
    return ndimage.gaussian_filter1d(Sxx, sigma=sigma_samples, axis=-1)

def compute_relative_power(lfp, fs, nperseg, noverlap, config):
    """
    Computes relative dB change for an omission window.
    lfp: (trials, time)
    config: {'start', 'end'} relative to P1=1000
    """
    t_start = 1000 + config['start']
    t_end = 1000 + config['end']
    
    # Extract window
    window_data = lfp[:, t_start:t_end]
    n_trials, n_time = window_data.shape
    
    # Compute TFR for each trial
    trial_tfrs = []
    for t in range(n_trials):
        f, t_vec, Sxx = signal.spectrogram(window_data[t], fs=fs, window='hann', 
                                         nperseg=nperseg, noverlap=noverlap)
        # Smoothing (20ms)
        Sxx_smooth = smooth_tfr(Sxx, GAUSS_SIGMA_SAMPLES)
        trial_tfrs.append(Sxx_smooth)
    
    trial_tfrs = np.array(trial_tfrs) # (trials, freqs, time)
    
    # Baseline: Average power during d(k-1) and d(k)
    # d(k-1) is first ~500ms, d(k) is last ~500ms
    # Index in t_vec
    t_ms = t_vec * 1000
    idx_baseline = np.where((t_ms < 500) | (t_ms > 1031))[0]
    
    avg_trial_tfr = np.mean(trial_tfrs, axis=0) # (freqs, time)
    baseline_power = np.mean(avg_trial_tfr[:, idx_baseline], axis=1, keepdims=True)
    
    # Relative dB: 10 * log10(P / P_baseline)
    rel_db = 10 * np.log10(avg_trial_tfr / (baseline_power + 1e-12))
    
    # SEM calculation for frequency bands
    # Let's pick standard bands for the trace plot
    bands = {'Theta': (4, 8), 'Alpha': (8, 13), 'Beta': (13, 30), 'Gamma': (35, 80)}
    traces = {}
    
    for name, (f_min, f_max) in bands.items():
        f_idx = np.where((f >= f_min) & (f <= f_max))[0]
        # Average power in band per trial then convert to dB
        trial_band_power = np.mean(trial_tfrs[:, f_idx, :], axis=1) # (trials, time)
        # We need trial-specific baseline for SEM
        trial_baseline = np.mean(trial_band_power[:, idx_baseline], axis=1, keepdims=True)
        trial_db = 10 * np.log10(trial_band_power / (trial_baseline + 1e-12))
        
        traces[name] = {
            'mean': np.nanmean(trial_db, axis=0),
            'sem': np.nanstd(trial_db, axis=0) / np.sqrt(n_trials),
            'time': t_ms - 500 # Align omission to 0ms (d-k-1 is -500 to 0)
        }
        
    return traces

def run_omission_dynamics():
    data_dir = r'D:\Analysis\Omission\local-workspace\data\arrays'
    output_dir = r'D:\Analysis\Omission\local-workspace\figures\part01'
    os.makedirs(output_dir, exist_ok=True)
    
    # Mapping sessions
    sessions = ['230630', '230816', '230830']
    
    for sid in sessions:
        # For simplicity, let's process V1 and PFC probes
        # We search for files like 'ses230816-probe0-lfp-AAAX.npy'
        lfp_files = glob.glob(os.path.join(data_dir, f'ses{sid}-probe*-lfp-*.npy'))
        
        for f_path in lfp_files:
            fname = os.path.basename(f_path)
            # Parse condition
            cond = fname.split('-')[-1].replace('.npy', '')
            probe = fname.split('-')[1].replace('probe', '')
            
            # Determine which omission it is
            target_p = None
            if cond in ['AXAB', 'BXBA', 'RXRR']: target_p = 'p2'
            elif cond in ['AAXB', 'BBXA', 'RRXR']: target_p = 'p3'
            elif cond in ['AAAX', 'BBBX', 'RRRX']: target_p = 'p4'
            
            if not target_p: continue
            
            print(f"🏺 Analyzing {fname} | Target: {target_p}")
            lfp = np.load(f_path, mmap_mode='r')
            
            # Use channel 64 (middle) as representative for now
            traces = compute_relative_power(lfp[:, 64, :], FS, NPERSEG, NOVERLAP, OMISSION_CONFIGS[target_p])
            
            # Plot
            fig = go.Figure()
            colors = {'Theta': 'cyan', 'Alpha': 'lime', 'Beta': GOLD, 'Gamma': VIOLET}
            
            for name, data in traces.items():
                t = data['time']
                mu = data['mean']
                sem = data['sem']
                
                # Shaded SEM
                fig.add_trace(go.Scatter(
                    x=np.concatenate([t, t[::-1]]),
                    y=np.concatenate([mu + sem, (mu - sem)[::-1]]),
                    fill='toself',
                    fillcolor=colors[name],
                    opacity=0.2,
                    line=dict(color='rgba(255,255,255,0)'),
                    name=f"{name} SEM",
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=t, y=mu,
                    name=name,
                    line=dict(color=colors[name], width=3)
                ))
            
            # Vertical lines for d(k-1), p(k), d(k)
            # p(k) onset is at 0 relative to d(k-1) end (approx 531ms window)
            # Wait, d(k-1) is ~531ms. If we align p(k) to 0:
            # d(k-1) is -531 to 0. p(k) is 0 to 500. d(k) is 500 to 1031.
            fig.add_vline(x=0, line_dash="dash", line_color="white", annotation_text="Omission Onset")
            fig.add_vline(x=500, line_dash="dash", line_color="white", annotation_text="Omission End")
            
            fig.update_layout(
                title=f"🏺 Omission Relative Power (dB) | {sid} P{probe} {cond}",
                xaxis_title="Time (ms)",
                yaxis_title="Relative Power Change (dB)",
                template="plotly_dark",
                paper_bgcolor=BLACK, plot_bgcolor=BLACK,
                font=dict(color=GOLD, family="Consolas")
            )
            
            out_name = f"OMIT_POWER_{sid}_P{probe}_{cond}.html"
            fig.write_html(os.path.join(output_dir, out_name))
            fig.write_image(os.path.join(output_dir, out_name.replace('.html', '.png')))
            print(f"  - Saved: {out_name}")

if __name__ == '__main__':
    run_omission_dynamics()
