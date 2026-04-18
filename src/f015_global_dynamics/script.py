# core
from src.analysis.io.loader import DataLoader
from src.f012_mi_matrix.analysis import analyze_mi_connectivity
from src.f015_global_dynamics.plot import plot_global_mi_dynamics

def run_f015():
    loader = DataLoader()
    sessions = ["230629", "230630", "230714", "230719"]
    areas = loader.CANONICAL_AREAS
    tensor = analyze_mi_connectivity(loader, sessions, areas)
    plot_global_mi_dynamics(tensor)

if __name__ == "__main__":
    run_f015()
