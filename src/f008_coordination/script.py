# core
from src.analysis.io.loader import DataLoader
from src.f008_coordination.analysis import analyze_spectral_harmony
from src.f008_coordination.plot import plot_spectral_harmony

def run_f008():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_spectral_harmony(loader, areas)
    plot_spectral_harmony(results, areas)

if __name__ == "__main__":
    run_f008()
