# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f033_spike_field_coherence.analysis import analyze_spike_field_coherence
from src.f033_spike_field_coherence.plot import plot_spike_field_coherence

def run_f033():
    """
    Main execution entry for Figure 33: Spike-Field Coherence.
    """
    log.progress("Starting Analysis f033: Spike-Field Coherence")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f033_spike_field_coherence")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_spike_field_coherence(loader, areas)
    
    if results:
        plot_spike_field_coherence(results, output_dir)
        
    log.progress("Analysis f033 complete.")

if __name__ == "__main__":
    run_f033()
