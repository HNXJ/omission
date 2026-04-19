from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f012_mi_matrix.analysis import analyze_mi_connectivity
from src.f012_mi_matrix.plot import plot_mi_matrix

def run_f012():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f012_mi_matrix")
    sessions = ["230629", "230630", "230714", "230719"]
    areas = loader.CANONICAL_AREAS
    tensor = analyze_mi_connectivity(loader, sessions, areas)
    plot_mi_matrix(tensor, areas, output_dir=output_dir)

if __name__ == "__main__":
    run_f012()
