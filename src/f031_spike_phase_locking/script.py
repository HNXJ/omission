# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f031_spike_phase_locking.analysis import analyze_spike_phase_locking
from src.f031_spike_phase_locking.plot import plot_spike_phase_locking

def run_f031():
    """
    Main execution entry for Figure 31: Spike-Field Phase Locking.
    """
    log.progress("Starting Analysis f031: Spike-Field Phase Locking")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f031_spike_phase_locking")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_spike_phase_locking(loader, areas, condition="AXAB")
    
    if results:
        plot_spike_phase_locking(results, output_dir)
        
    log.progress("Analysis f031 complete.")

if __name__ == "__main__":
    run_f031()
