"""
lfp_tfr.py
Spectral analysis for Omission task (TFR, Band Power).
"""
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
from scipy.signal import spectrogram
from codes.functions.lfp.lfp_constants import DEFAULT_WF_PARAMS, FS_LFP, BANDS


def compute_tfr(epoch: np.ndarray, fs: float = FS_LFP):
    """
    Computes trial-wise TFR using spectrogram (Hanning, 98% overlap).
    epoch: (trials, time)
    Returns: freqs, times_ms, power (trials, freqs, time)
    """
    if epoch.size == 0:
        return np.array([]), np.array([]), np.array([[[]]])
    if epoch.ndim == 1:
        epoch = epoch[None, :]
        
    f, t, sxx = spectrogram(epoch, fs=fs, window=DEFAULT_WF_PARAMS["window"],
                            nperseg=DEFAULT_WF_PARAMS["nperseg"],
                            noverlap=DEFAULT_WF_PARAMS["noverlap"],
                            scaling="density", mode="psd")
    t_ms = t * 1000.0
    return f, t_ms, 10.0 * np.log10(sxx + 1e-12)


def compute_multitaper_tfr(data, fs=1000.0, nperseg=256, noverlap=250):
    """Alias for compute_tfr to maintain repo compatibility."""
    return compute_tfr(data, fs, nperseg, noverlap)


def get_band_power(freqs: np.ndarray, power: np.ndarray, band_limits: Tuple[int, int]) -> np.ndarray:
    """Extracts mean power for a specific band (Step 7)."""
    mask = (freqs >= band_limits[0]) & (freqs <= band_limits[1])
    if power.ndim == 3: # (trials, freqs, time)
        return np.nanmean(power[:, mask, :], axis=1)
    return np.nanmean(power[mask, :], axis=0)


def collapse_band_power(freqs: np.ndarray, power: np.ndarray) -> Dict[str, np.ndarray]:
    """Collapses TFR into trajectories for all predefined bands."""
    out: Dict[str, np.ndarray] = {}
    if freqs.size == 0 or power.size == 0:
        return out
    for band, lims in BANDS.items():
        out[band] = get_band_power(freqs, power, lims)
    return out
