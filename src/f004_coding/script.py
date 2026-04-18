# core
from src.analysis.io.loader import DataLoader
from src.f004_coding.analysis import analyze_population_manifolds
from src.f004_coding.plot import plot_population_manifolds

def run_f004():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_population_manifolds(loader, areas)
    plot_population_manifolds(results)

if __name__ == "__main__":
    run_f004()
