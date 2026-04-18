# core
from src.analysis.io.loader import DataLoader
from src.f005_tfr.analysis import analyze_area_tfrs
from src.f005_tfr.plot import plot_area_tfrs

def run_f005():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    results = analyze_area_tfrs(areas)
    plot_area_tfrs(results)

if __name__ == "__main__":
    run_f005()
