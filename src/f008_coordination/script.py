from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f008_coordination.analysis import analyze_spectral_harmony
from src.f008_coordination.plot import plot_spectral_harmony

def run_f008():
    log.progress("Starting Analysis f008: Spectral Harmony (Band Power Correlation)")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f008_coordination")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_spectral_harmony(loader, areas)
    if results:
        plot_spectral_harmony(results, areas, output_dir=str(output_dir))
    log.progress("Analysis f008 complete.")

if __name__ == "__main__":
    run_f008()
