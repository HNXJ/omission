# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.f012_mi_matrix.analysis import analyze_mi_connectivity

def analyze_global_mi_dynamics(loader: DataLoader, sessions: list, areas: list):
    """
    Computes global mean MI dynamics (Reuse f012 logic).
    """
    return analyze_mi_connectivity(loader, sessions, areas)
