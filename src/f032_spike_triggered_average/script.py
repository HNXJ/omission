# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f032_spike_triggered_average.analysis import analyze_spike_triggered_average
from src.f032_spike_triggered_average.plot import plot_spike_triggered_average

def run_f032():
    """
    Main execution entry for Figure 32: Spike-Triggered Average.
    """
    log.progress("Starting Analysis f032: Spike-Triggered Average")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f032_spike_triggered_average")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_spike_triggered_average(loader, areas)
    
    if results:
        plot_spike_triggered_average(results, output_dir)
        
    log.progress("Analysis f032 complete.")

if __name__ == "__main__":
    run_f032()
