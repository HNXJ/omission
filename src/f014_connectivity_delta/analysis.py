# core
from src.analysis.io.loader import DataLoader
from src.f012_mi_matrix.analysis import analyze_mi_connectivity

def analyze_connectivity_delta(loader: DataLoader, sessions: list, areas: list):
    """
    Computes connectivity for AXAB and AAAB (Reuse f012 logic).
    """
    return analyze_mi_connectivity(loader, sessions, areas)
