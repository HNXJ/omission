# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f033_global_synthesis.analysis import analyze_global_synthesis
from src.f033_global_synthesis.plot import plot_global_synthesis

def run_f033():
    """
    Main execution entry for Figure 33.
    """
    log.progress("Starting Analysis f033: Global Synthesis")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f033_global_synthesis")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_global_synthesis(loader, areas)
    
    plot_global_synthesis(results, areas, output_dir)
    log.progress("Analysis f033 complete.")

if __name__ == "__main__":
    run_f033()
