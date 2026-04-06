
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
# Gamma-Standard timings: p1=1000, d1=1531, p2=2031, d2=2562, p3=3062, d3=3593, p4=4093, d4=4624
OMISSION_CONFIGS = {
    'p2': {'start': 1031, 'end': 1562, 'label': 'AXAB/BXBA/RXRR'},
    'p3': {'start': 2062, 'end': 2593, 'label': 'AAXB/BBXA/RRXR'},
    'p4': {'start': 3093, 'end': 3624, 'label': 'AAAX/BBBX/RRRX'}
}

# TFR Parameters
BANDS = {'Theta': (4, 8), 'Alpha': (8, 13), 'Beta': (15, 25), 'Gamma': (35, 70)}

def compute_relative_power(lfp, fs, nperseg, noverlap, config):
    """
    Computes relative dB change for an omission window.
    lfp: (trials, time)
    config: {'start', 'end'} relative to P1=1000
    """
    t_start = 1000 + config['start']
    t_end = 1000 + config['end']
    
    # Extract window
    window_data = np.nan_to_num(lfp[:, t_start:t_end])
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
    t_ms = t_vec * 1000
    idx_baseline = np.where((t_ms < 500) | (t_ms > 1031))[0]
    
    avg_trial_tfr = np.mean(trial_tfrs, axis=0)
    baseline_power = np.mean(avg_trial_tfr[:, idx_baseline], axis=1, keepdims=True)
    
    rel_db = 10 * np.log10(avg_trial_tfr / (baseline_power + 1e-12))
    
    traces = {}
    for name, (f_min, f_max) in BANDS.items():
        f_idx = np.where((f >= f_min) & (f <= f_max))[0]
        trial_band_power = np.mean(trial_tfrs[:, f_idx, :], axis=1)
        trial_baseline = np.mean(trial_band_power[:, idx_baseline], axis=1, keepdims=True)
        trial_db = 10 * np.log10(trial_band_power / (trial_baseline + 1e-12))
        
        traces[name] = {
            'mean': np.nanmean(trial_db, axis=0),
            'sem': np.nanstd(trial_db, axis=0) / np.sqrt(n_trials),
            'time': t_ms - 500
        }
    return traces

def run_omission_dynamics():
    # ... (setup remains same)
    
            # Use channel 64 (middle) as representative for now
            lfp_data = np.nan_to_num(np.load(f_path, mmap_mode='r'))
            traces = compute_relative_power(lfp_data[:, 64, :], FS, NPERSEG, NOVERLAP, OMISSION_CONFIGS[target_p])
            
            # Plot
            fig = go.Figure()
            colors = {'Theta': 'cyan', 'Alpha': 'lime', 'Beta': 'gold', 'Gamma': 'violet'}
            
            # ... (trace plotting remains same)
            
            fig.add_vline(x=0, line_dash="dash", line_color="black", annotation_text="Omission Onset")
            fig.add_vline(x=500, line_dash="dash", line_color="black", annotation_text="Omission End")
            
            fig.update_layout(
                title=f"🏺 Omission Relative Power (dB) | {sid} P{probe} {cond}",
                xaxis_title="Time (ms)",
                yaxis_title="Relative Power Change (dB)",
                template="plotly_white"
            )
            
            out_name = f"OMIT_POWER_{sid}_P{probe}_{cond}.html"
            fig.write_html(os.path.join(output_dir, out_name))
            fig.write_image(os.path.join(output_dir, out_name.replace('.html', '.png')))
            print(f"  - Saved: {out_name}")


def main(args=None):
    run_omission_dynamics()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
