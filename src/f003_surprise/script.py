# core
from src.analysis.io.loader import DataLoader
from src.f003_surprise.analysis import analyze_area_psths
from src.f003_surprise.plot import plot_area_psths

def run_f003():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_area_psths(loader, areas)
    plot_area_psths(results)

if __name__ == "__main__":
    run_f003()
