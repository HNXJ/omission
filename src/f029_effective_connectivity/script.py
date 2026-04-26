from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f029_effective_connectivity.analysis import analyze_granger_causality
from src.f029_effective_connectivity.plot import plot_granger_causality

def run_f029():
    log.progress("Starting Analysis f029: Effective Connectivity (Granger Causality)")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f029_effective_connectivity")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_granger_causality(areas, maxlag=20)
    
    if results:
        plot_granger_causality(results, output_dir=str(output_dir))
        log.progress("Analysis f029 complete.")
    else:
        log.error("Analysis f029 failed: No results generated.")

if __name__ == "__main__":
    run_f029()
