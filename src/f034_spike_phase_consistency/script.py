# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f034_spike_phase_consistency.analysis import analyze_ppc_spectrum
from src.f034_spike_phase_consistency.plot import plot_ppc_spectrum

def run_f034():
    """
    Main execution entry for Figure 34: Spike-Field PPC.
    """
    log.progress("Starting Analysis f034: Spike-Field PPC")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f034_spike_phase_consistency")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_ppc_spectrum(loader, areas)
    
    if results:
        plot_ppc_spectrum(results, output_dir)
        
    log.progress("Analysis f034 complete.")

if __name__ == "__main__":
    run_f034()
