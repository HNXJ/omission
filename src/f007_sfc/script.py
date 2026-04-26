from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f007_sfc.analysis import analyze_sfc_plv
from src.f007_sfc.plot import plot_sfc_plv

def run_f007():
    log.progress("Starting Analysis f007: Spike-Field Coherence (PLV Spectrum)")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f007_sfc")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_sfc_plv(loader, areas)
    if results:
        plot_sfc_plv(results, output_dir=str(output_dir))
    log.progress("Analysis f007 complete.")

if __name__ == "__main__":
    run_f007()
