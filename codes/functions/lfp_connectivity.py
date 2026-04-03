"""
lfp_connectivity.py
Pairwise and directed connectivity (Steps 9-11).
"""
import numpy as np
from scipy import signal

def compute_pairwise_coherence(sig_a, sig_b, fs=1000.0):
    """
    Computes coherence (Step 9).
    sig_a/b: (trials, time)
    """
    f, Cxy = signal.coherence(sig_a, sig_b, fs=fs, nperseg=256)
    return f, Cxy

def compute_granger_causality(sig_a, sig_b, fs=1000.0):
    """
    Placeholder for Granger (Step 11).
    Real implementation in run_figure_06_directionality.py
    """
    return None
