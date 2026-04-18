# core
from src.analysis.io.loader import DataLoader
from src.f006_band_power.analysis import analyze_band_dynamics
from src.f006_band_power.plot import plot_band_dynamics

def run_f006():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_band_dynamics(areas)
    plot_band_dynamics(results)

if __name__ == "__main__":
    run_f006()
