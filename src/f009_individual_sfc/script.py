from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f009_individual_sfc.analysis import analyze_individual_sfc
from src.f009_individual_sfc.plot import plot_individual_sfc

def run_f009():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f009_individual_sfc")
    areas = loader.CANONICAL_AREAS
    results = analyze_individual_sfc(loader, areas)
    plot_individual_sfc(results, output_dir=output_dir)

if __name__ == "__main__":
    run_f009()
