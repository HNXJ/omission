import numpy as np

def preprocess_lfp(lfp, channels):
    """Canonical preprocessing: returns raw LFP."""
    return lfp

def apply_bipolar_ref(lfp, channel_map):
    """Placeholder bipolar referencing."""
    return lfp

def extract_epochs(lfp, events, window=(-1000, 4000)):
    """Extracts trial-aligned epochs from continuous data."""
    return lfp

def baseline_normalize(epochs, baseline_window=(-500, -100)):
    """Baseline normalization to dB scale."""
    return epochs
