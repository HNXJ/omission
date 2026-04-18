# core
from src.analysis.io.loader import DataLoader
from src.f010_sfc_delta.analysis import analyze_sfc_delta
from src.f010_sfc_delta.plot import plot_sfc_delta

def run_f010():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_sfc_delta(loader, areas)
    plot_sfc_delta(results)

if __name__ == "__main__":
    run_f010()
