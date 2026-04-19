# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f040_population_sync_index.analysis import analyze_population_sync_index
from src.f040_population_sync_index.plot import plot_population_sync_index

def run_f040():
    """
    Main execution entry for Figure 40: PSI.
    """
    log.progress("Starting Analysis f040: Population Synchronization Index")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f040_population_sync_index")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_population_sync_index(loader, areas)
    
    if results:
        plot_population_sync_index(results, output_dir)
        
    log.progress("Analysis f040 complete.")

if __name__ == "__main__":
    run_f040()
