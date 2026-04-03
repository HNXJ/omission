"""
lfp_preproc.py
LFP Preprocessing for Omission task (Step 3).
"""
import numpy as np

def apply_bipolar_ref(lfp: np.ndarray):
    """
    Apply bipolar derivation to reduce volume conduction (Step 3).
    lfp: (trials, channels, time)
    """
    # Assuming channels are ordered spatially
    return lfp[:, :-1, :] - lfp[:, 1:, :]

def reject_bad_channels(lfp: np.ndarray, thresh: float = 3.5):
    """
    QC and artifact rejection (Step 3).
    """
    # Compute channel-wise variance across time
    # Reject those beyond the threshold
    return lfp
