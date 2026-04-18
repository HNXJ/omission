# core
from src.analysis.io.loader import DataLoader
from src.f011_laminar.analysis import analyze_laminar_routing
from src.f011_laminar.plot import plot_laminar_routing

def run_f011():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_laminar_routing(loader, areas)
    plot_laminar_routing(results)

if __name__ == "__main__":
    run_f011()
