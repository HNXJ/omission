from pathlib import Path
# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f029_info_bottleneck.analysis import analyze_information_bottleneck
from src.f029_info_bottleneck.plot import plot_information_bottleneck

def run_f029():
    """
    Main execution entry for Figure 29.
    """
    log.progress("Starting Analysis f029: Information Bottleneck")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f029_info_bottleneck")
    
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    results = analyze_information_bottleneck(loader, sessions, areas)
    if results:
        plot_information_bottleneck(results, output_dir=output_dir)
    
    log.progress("Analysis f029 complete.")

if __name__ == "__main__":
    run_f029()
