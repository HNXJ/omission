# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f035_spike_triggered_spectrum.analysis import analyze_spike_triggered_spectrum
from src.f035_spike_triggered_spectrum.plot import plot_spike_triggered_spectrum

def run_f035():
    """
    Main execution entry for Figure 35: STS.
    """
    log.progress("Starting Analysis f035: Spike-Triggered Spectrum")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f035_spike_triggered_spectrum")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_spike_triggered_spectrum(loader, areas)
    
    if results:
        plot_spike_triggered_spectrum(results, output_dir)
        
    log.progress("Analysis f035 complete.")

if __name__ == "__main__":
    run_f035()
