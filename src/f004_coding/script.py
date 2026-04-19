from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f004_coding.analysis import analyze_population_manifolds
from src.f004_coding.plot import plot_population_manifolds

def run_f004():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f004_coding")
    areas = loader.CANONICAL_AREAS
    results = analyze_population_manifolds(loader, areas)
    plot_population_manifolds(results, output_dir=output_dir)

if __name__ == "__main__":
    run_f004()
