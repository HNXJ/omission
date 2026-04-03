"""
lfp_tfr.py
Mathematical core for Time-Frequency Representations (Step 6).
"""
import numpy as np
from scipy import signal

def compute_multitaper_tfr(data, fs=1000.0, nperseg=256, noverlap=250):
    """
    Computes TFR using spectrogram (Step 6).
    data: (trials, time)
    Returns: freqs, times, power (freqs x time)
    """
    # Average across trials to get induced/evoked power depending on subtraction
    f, t, Sxx = signal.spectrogram(data, fs=fs, nperseg=nperseg, noverlap=noverlap, scaling='density')
    avg_pwr = np.mean(Sxx, axis=0) # (freqs, time)
    return f, t, avg_pwr

def get_band_power(freqs, pwr_tfr, band_limits):
    """
    Extracts mean power for a specific band (Step 7).
    """
    mask = (freqs >= band_limits[0]) & (freqs <= band_limits[1])
    return np.mean(pwr_tfr[mask, :], axis=0)
