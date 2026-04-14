"""
lfp_tfr.py — Canonical Multitaper TFR Engine
Implements trial-preserved high-fidelity spectral analysis.
"""
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import mne
from mne.time_frequency import tfr_array_multitaper
from codes.functions.lfp.lfp_constants import FS_LFP, BANDS

def compute_multitaper_tfr(
    data: np.ndarray, 
    fs: float = FS_LFP, 
    freqs: np.ndarray = np.arange(4, 81, 2), 
    n_cycles: float | np.ndarray = 7
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes high-fidelity multitaper TFR.
    data: (trials, channels, time)
    Returns: freqs, times_ms, power (trials, channels, freqs, time)
    """
    if data.ndim == 2:
        data = data[None, :, :]
    
    # Ensure float64
    data = data.astype(np.float64)
    
    # MNE TFR multitaper: (trials, channels, freqs, time)
    power = tfr_array_multitaper(data, sfreq=fs, freqs=freqs, n_cycles=n_cycles, 
                                 output='power', use_fft=True, verbose=False)
    
    times_ms = np.linspace(0, data.shape[-1]/fs*1000, data.shape[-1])
    
    return freqs, times_ms, 10.0 * np.log10(power + 1e-12)

def get_band_power(freqs: np.ndarray, power: np.ndarray, band_limits: Tuple[int, int]) -> np.ndarray:
    """Extracts mean power for a specific band across channels."""
    mask = (freqs >= band_limits[0]) & (freqs <= band_limits[1])
    # power: (trials, channels, freqs, time)
    # collapse freqs
    return np.nanmean(power[..., mask, :], axis=-2)

def collapse_band_power(freqs: np.ndarray, power: np.ndarray) -> Dict[str, np.ndarray]:
    """Collapses TFR into trajectories for all predefined bands."""
    out: Dict[str, np.ndarray] = {}
    for band, lims in BANDS.items():
        out[band] = get_band_power(freqs, power, lims)
    return out
