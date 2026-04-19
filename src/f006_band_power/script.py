from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f006_band_power.analysis import analyze_band_dynamics
from src.f006_band_power.plot import plot_band_dynamics

def run_f006():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f006_band_power")
    areas = loader.CANONICAL_AREAS
    results = analyze_band_dynamics(areas)
    plot_band_dynamics(results, output_dir=output_dir)

if __name__ == "__main__":
    run_f006()
