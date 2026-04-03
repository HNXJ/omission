"""
lfp_tfr.py
Mathematical core for Time-Frequency Representations (Step 6).
"""
import numpy as np
from scipy import signal

def compute_multitaper_tfr(data, fs=1000.0, nperseg=256, noverlap=250):
    """
    Computes trial-wise TFR using spectrogram.
    data: (trials, time)
    Returns: freqs, times, power (trials x freqs x time)
    """
    # Use scipy.signal.spectrogram on the full data
    # (trials, time) -> (trials, freqs, times)
    f, t, Sxx = signal.spectrogram(data, fs=fs, nperseg=nperseg, noverlap=noverlap, scaling='density')
    return f, t, Sxx

def get_band_power(freqs, pwr_tfr, band_limits):
    """
    Extracts mean power for a specific band.
    pwr_tfr: (trials, freqs, time) or (freqs, time)
    """
    mask = (freqs >= band_limits[0]) & (freqs <= band_limits[1])
    if pwr_tfr.ndim == 3:
        return np.mean(pwr_tfr[:, mask, :], axis=1)
    return np.mean(pwr_tfr[mask, :], axis=0)
