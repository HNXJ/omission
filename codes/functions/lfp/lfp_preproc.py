"""
lfp_preproc.py
LFP Preprocessing for Omission task (Bipolar, QC, Normalization).
"""
from __future__ import annotations
from typing import Any, Dict, Tuple
import numpy as np


def preprocess_lfp(lfp: np.ndarray, channels: Any = None) -> np.ndarray:
    """Minimal LFP preprocessing: float conversion and mean subtraction."""
    if lfp is None:
        return np.empty((0, 0, 0))
    x = np.asarray(lfp, dtype=float)
    if x.ndim >= 2:
        x = x - np.nanmean(x, axis=-1, keepdims=True)
    return x


def apply_bipolar_ref(lfp: np.ndarray) -> np.ndarray:
    """Apply bipolar derivation to reduce volume conduction (Step 3)."""
    if lfp.ndim != 3: # (trials, channels, time)
        return lfp
    return lfp[:, :-1, :] - lfp[:, 1:, :]


def baseline_normalize(epoch: np.ndarray, baseline_slice: slice) -> np.ndarray:
    """Percent change relative to baseline mean."""
    if epoch.size == 0:
        return epoch
    base = np.nanmean(epoch[..., baseline_slice], axis=-1, keepdims=True)
    return 100.0 * (epoch - base) / (np.abs(base) + 1e-9)


def extract_epochs(lfp: np.ndarray, event_times: np.ndarray, window_ms: Tuple[int, int] = (-500, 1000), fs: float = 1000.0) -> np.ndarray:
    \"\"\"
    Extract aligned epochs from LFP signal based on provided event times.
    
    Args:
        lfp (np.ndarray): Signal array of shape (channels, time).
        event_times (np.ndarray): Array of event onset times in seconds.
        window_ms (Tuple[int, int]): Time window around event in ms.
        fs (float): Sampling frequency in Hz.
        
    Returns:
        np.ndarray: Epoch array of shape (events, channels, time_samples).
    \"\"\"
    # 1. Convert window to samples
    start_samp = int(window_ms[0] * fs / 1000.0)
    end_samp = int(window_ms[1] * fs / 1000.0)
    
    # 2. Extract epochs
    epochs = []
    for t in event_times:
        idx = int(t * fs)
        start = idx + start_samp
        end = idx + end_samp
        
        # Check boundaries
        if start < 0 or end > lfp.shape[1]:
            continue
            
        epochs.append(lfp[:, start:end])
        
    return np.array(epochs)
