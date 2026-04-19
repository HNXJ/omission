from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f010_sfc_delta.analysis import analyze_sfc_delta
from src.f010_sfc_delta.plot import plot_sfc_delta

def run_f010():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f010_sfc_delta")
    areas = loader.CANONICAL_AREAS
    results = analyze_sfc_delta(loader, areas)
    plot_sfc_delta(results, output_dir=output_dir)

if __name__ == "__main__":
    run_f010()
