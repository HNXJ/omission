from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f011_laminar.analysis import analyze_laminar_routing
from src.f011_laminar.plot import plot_laminar_routing

def run_f011():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f011_laminar")
    areas = loader.CANONICAL_AREAS
    results = analyze_laminar_routing(loader, areas)
    plot_laminar_routing(results, output_dir=output_dir)

if __name__ == "__main__":
    run_f011()
