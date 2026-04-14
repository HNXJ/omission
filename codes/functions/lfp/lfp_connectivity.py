"""
lfp_connectivity.py
Pairwise and directed connectivity (Coherence, Granger).
"""
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
from scipy.signal import coherence
from codes.functions.lfp.lfp_constants import FS_LFP


def compute_coherence(sig1: np.ndarray, sig2: np.ndarray, fs: float = FS_LFP):
    """Coherence spectrum for one area pair."""
    if sig1.size == 0 or sig2.size == 0:
        return np.array([]), np.array([])
    f, cxy = coherence(sig1, sig2, fs=fs, nperseg=256)
    return f, cxy


def compute_pairwise_coherence(sig_a, sig_b, fs=1000.0):
    """Alias for compute_coherence to maintain repo compatibility."""
    return compute_coherence(sig_a, sig_b, fs)


def compute_granger(*args, **kwargs):
    \"\"\"
    Directionality/Granger causality calculation.
    
    WARNING: Not currently implemented in the canonical repository.
    
    Raises:
        NotImplementedError: Always, as this functionality is not yet available.
    \"\"\"
    raise NotImplementedError("Placeholder: Granger not implemented in canonical path")
import numpy as np
from scipy.signal import hilbert

def compute_pac(phase_signal, amplitude_signal):
    """
    Computes Phase-Amplitude Coupling using the Modulation Index (Tort et al., 2010).
    Input: phase_signal (Time), amplitude_signal (Time)
    Output: Modulation Index (scalar)
    """
    # Bin phases and compute mean amplitude in each bin
    n_bins = 18
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    
    # Get phases
    phase = np.angle(hilbert(phase_signal))
    amp = np.abs(hilbert(amplitude_signal))
    
    mean_amp_in_bins = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (phase >= bins[i]) & (phase < bins[i+1])
        if np.sum(mask) > 0:
            mean_amp_in_bins[i] = np.mean(amp[mask])
            
    # Normalized amplitude distribution
    p = mean_amp_in_bins / np.sum(mean_amp_in_bins)
    
    # Entropy (H) and Modulation Index (MI)
    h_max = np.log(n_bins)
    h = -np.sum(p * np.log(p + 1e-12))
    mi = (h_max - h) / h_max
    
    return mi
