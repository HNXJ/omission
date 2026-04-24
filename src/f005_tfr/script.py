from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f005_tfr.analysis import analyze_area_tfrs
from src.f005_tfr.plot import plot_area_tfrs

def run_f005():
    log.progress("Starting Analysis f005: TFR Suite")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f005_tfr")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_area_tfrs(areas)
    if results:
        plot_area_tfrs(results, output_dir=str(output_dir))
    log.progress("Analysis f005 complete.")

if __name__ == "__main__":
    run_f005()
