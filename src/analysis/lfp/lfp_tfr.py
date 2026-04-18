# -*- coding: utf-8 -*-
"""
lfp_tfr.py - Canonical Multitaper TFR Engine
Implements trial-preserved high-fidelity spectral analysis.
"""
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import mne
from mne.time_frequency import tfr_array_multitaper
from src.analysis.lfp.lfp_constants import FS_LFP, BANDS

def compute_multitaper_tfr(
    data: np.ndarray, 
    fs: float = FS_LFP, 
    freqs: np.ndarray = np.arange(4, 81, 2), 
    n_cycles: float | np.ndarray = 7
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes TFR using multitaper. Returns linear power.
    data shape: (trials, channels, time)
    Returns: freqs, times_ms, power (trials, channels, freqs, times)
    """
    if data.ndim == 2:
        data = data[None, :, :]
    data = data.astype(np.float64)
    # output='power' returns linear power
    power = tfr_array_multitaper(data, sfreq=fs, freqs=freqs, n_cycles=n_cycles, 
                                 output='power', use_fft=True, verbose=False)
    times_ms = np.linspace(0, data.shape[-1]/fs*1000, data.shape[-1])
    return freqs, times_ms, power

# Alias for compatibility with legacy and user scripts
compute_tfr = compute_multitaper_tfr

def get_band_power(freqs: np.ndarray, power: np.ndarray, band_limits: Tuple[int, int]) -> np.ndarray:
    mask = (freqs >= band_limits[0]) & (freqs <= band_limits[1])
    return np.nanmean(power[..., mask, :], axis=-2)

def collapse_band_power(freqs: np.ndarray, power: np.ndarray) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for band, lims in BANDS.items():
        out[band] = get_band_power(freqs, power, lims)
    return out
