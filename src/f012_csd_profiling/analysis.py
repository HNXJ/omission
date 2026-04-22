# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.spiking.stats import compute_omission_connectivity_tensor

def analyze_mi_connectivity(loader: DataLoader, sessions: list, areas: list):
    """
    Computes the 17-frame connectivity tensor (MI).
    """
    bands = {"Theta": (4, 8), "Alpha": (8, 13), "Beta": (13, 30), "Gamma": (35, 80)}
    # Define frames relative to P1 onset (sample 1000)
    w = {
        "fx": slice(500, 1000), "p1": slice(1000, 1531), "d1": slice(1531, 2031),
        "p2": slice(2031, 2562), "d2": slice(2562, 3062), "p3": slice(3062, 3593),
        "d3": slice(3593, 4093), "p4": slice(4093, 4624), "d4": slice(4624, 5124)
    }
    frame_keys = ["fx", "p1", "d1", "p2", "d2", "p3", "d3", "p4", "d4"]
    frames = {k: w[k] for k in frame_keys}
    
    tensor, _ = compute_omission_connectivity_tensor(loader, sessions, areas, bands, frame_keys, frames)
    return tensor

def run_f012_analysis():
    loader = DataLoader()
    sessions = ["230629", "230630"] # Representative subset
    areas = loader.CANONICAL_AREAS
    return analyze_mi_connectivity(loader, sessions, areas)
