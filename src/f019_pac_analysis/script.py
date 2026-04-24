from pathlib import Path
# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f019_pac_analysis.analysis import analyze_pac
from src.f019_pac_analysis.plot import plot_pac_summary

def run_f019():
    """
    Main execution entry for Figure 19.
    """
    log.progress("Starting Analysis f019: PAC Analysis")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f019-pac-analysis")
    
    # Define sessions and areas to analyze
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    # 1. Run Analysis
    results = analyze_pac(loader, sessions, areas)
    
    # 2. Plot
    plot_pac_summary(results, output_dir=output_dir)
    
    log.progress("Analysis f019 complete.")

if __name__ == "__main__":
    run_f019()
