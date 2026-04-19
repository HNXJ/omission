# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f039_spike_field_granger.analysis import analyze_spike_field_granger
from src.f039_spike_field_granger.plot import plot_spike_field_granger

def run_f039():
    """
    Main execution entry for Figure 39: SPK-LFP Influence.
    """
    log.progress("Starting Analysis f039: Spike-Field Influence")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f039_spike_field_granger")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_spike_field_granger(loader, areas)
    
    if results:
        plot_spike_field_granger(results, output_dir)
        
    log.progress("Analysis f039 complete.")

if __name__ == "__main__":
    run_f039()
