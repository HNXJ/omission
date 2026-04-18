# core
from src.analysis.io.loader import DataLoader
from src.f007_sfc.analysis import analyze_sfc_plv
from src.f007_sfc.plot import plot_sfc_plv

def run_f007():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_sfc_plv(loader, areas)
    plot_sfc_plv(results)

if __name__ == "__main__":
    run_f007()
