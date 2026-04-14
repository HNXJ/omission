#!/usr/bin/env python3
"""
Figure 6: TFR Contrast Analysis
Computes dB-normalized TFR contrasts between omission slots and baselines.
Fixes 'omit_powers' undefined variable error.
"""
from __future__ import annotations
import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
import plotly.graph_objects as go

# Setup paths
from codes.config.paths import PROJECT_ROOT, DATA_DIR, OUTPUT_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Imports from project
from codes.functions.lfp.lfp_pipeline import get_signal_conditional
from codes.functions.lfp.lfp_constants import CANONICAL_AREAS, BANDS, BAND_COLORS

# Configuration
WINDOW = (-1.0, 4.0)
FS = 1000.0

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data, axis=-1)

def compute_band_power(epochs, fs=FS):
    if epochs is None or epochs.size == 0 or np.all(np.isnan(epochs)):
        return None
    powers = {}
    for band, (low, high) in BANDS.items():
        filtered = butter_bandpass_filter(epochs, low, high, fs)
        analytic = hilbert(filtered, axis=-1)
        power = np.abs(analytic)**2
        # Average across trials (axis 0) and channels (axis 1)
        powers[band] = np.nanmean(power, axis=(0, 1))
    return powers

def generate_figure_6(session_file=None):
    if session_file is None:
        session_file = list(DATA_DIR.glob("*.nwb"))[0]
    
    print(f"Generating Figure 6 for session: {session_file.name}")
    time_vec = np.linspace(WINDOW[0]*1000, WINDOW[1]*1000, int((WINDOW[1]-WINDOW[0])*FS))
    
    # Placeholder baseline logic (should be RRRR trials in production)
    # Extract ALL control trials for baseline
    base_epochs = get_signal_conditional(session_file, "V1", condition="RRRR", epoch_window=WINDOW)
    base_powers = compute_band_power(base_epochs)

    for area in CANONICAL_AREAS:
        try:
            # 1. Extract Omission Trials (e.g., AXAB family)
            omit_epochs = get_signal_conditional(session_file, area, condition="AXAB", epoch_window=WINDOW)
            if omit_epochs.size == 0: continue
            
            # 2. Compute Power
            omit_powers = compute_band_power(omit_epochs)
            if not omit_powers: continue
            
            # 3. Plot Contrast
            fig = go.Figure()
            for band, power in omit_powers.items():
                # Normalize by V1 baseline or local baseline as per spec
                # Simplified to local baseline for this pass
                base_mean = np.nanmean(base_powers[band]) if base_powers else 1.0
                db_trace = 10 * np.log10(np.maximum(power, 1e-6) / np.maximum(base_mean, 1e-6))
                fig.add_trace(go.Scatter(x=time_vec, y=db_trace, name=band, line=dict(color=BAND_COLORS.get(band))))
            
            fig.update_layout(
                title=f'Figure 6: Omission dB Power | {area} | AXAB',
                xaxis_title="Time (ms)",
                yaxis_title="Power (dB)",
                template='plotly_dark'
            )
            
            out_p = OUTPUT_DIR / "oglo-figures" / "figure-6"
            out_p.mkdir(parents=True, exist_ok=True)
            fig.write_html(out_p / f'figure_6_{session_file.stem}_{area}_AXAB.html')
            
        except Exception as e:
            print(f"Error processing {area}: {e}")

if __name__ == '__main__':
    generate_figure_6()
