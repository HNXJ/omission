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
    """Directionality placeholder. (Step 11)."""
    return np.empty((0, 0))
