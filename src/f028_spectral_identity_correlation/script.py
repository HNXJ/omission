from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f028_spectral_identity_correlation.analysis import analyze_spectral_identity_correlation
from src.f028_spectral_identity_correlation.plot import plot_spectral_identity_correlation

def run_f028():
    log.progress("Starting Analysis f028: Spectral-Identity Correlation")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f028_spectral_identity")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_spectral_identity_correlation(areas)
    
    if results:
        plot_spectral_identity_correlation(results, output_dir=str(output_dir))
        log.progress("Analysis f028 complete.")
    else:
        log.error("Analysis f028 failed: No results generated.")

if __name__ == "__main__":
    run_f028()
