"""
lfp_io.py
I/O utilities for NWB-LFP data extraction.
"""
from pathlib import Path
import numpy as np

def load_lfp_session(nwb_path: Path):
    """
    Returns (LFP Tensor, Channel Table, Trial Table).
    Ensures mandatory np.nan_to_num for data loading (Sanitation).
    """
    # Placeholder for pynwb loading
    return None, None, None

def save_lfp_results(out_path: Path, data: dict, metadata: dict = None):
    """
    Saves spectral data and .metadata.json sidecar.
    """
    # Placeholder for saving
    pass
