# core
from src.analysis.io.loader import DataLoader
from src.f012_mi_matrix.analysis import analyze_mi_connectivity
from src.f014_connectivity_delta.plot import plot_connectivity_delta

def run_f014():
    loader = DataLoader()
    sessions = ["230629", "230630", "230714", "230719"]
    areas = loader.CANONICAL_AREAS
    tensor = analyze_mi_connectivity(loader, sessions, areas)
    plot_connectivity_delta(tensor, areas)

if __name__ == "__main__":
    run_f014()
