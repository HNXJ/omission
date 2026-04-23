# core
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f040_onset_latency.analysis import analyze_onset_latency
from src.f040_onset_latency.plot import plot_onset_latency

def run_f040():
    """
    Main entry point for Figure 40: Onset Latency.
    """
    log.progress("Starting Analysis f040: Onset Latency")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f040-onset-latency")
    
    # Analyze all canonical areas
    areas = loader.CANONICAL_AREAS
    results = analyze_onset_latency(loader, areas)
    
    if results:
        plot_onset_latency(results, str(output_dir))
        
    log.progress("Analysis f040 complete.")

if __name__ == "__main__":
    run_f040()
