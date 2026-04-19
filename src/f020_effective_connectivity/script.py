from pathlib import Path
# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f020_effective_connectivity.analysis import analyze_effective_connectivity
from src.f020_effective_connectivity.plot import plot_effective_connectivity

def run_f020():
    """
    Main execution entry for Figure 20.
    """
    log.progress("Starting Analysis f020: Effective Connectivity")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f020_effective_connectivity")
    
    # Define sessions and area pairs
    sessions = ["230629", "230630", "230714", "230719"]
    area_pairs = [("V1", "V4"), ("V4", "PFC"), ("PFC", "FEF")]
    
    # 1. Run Analysis
    results = analyze_effective_connectivity(loader, sessions, area_pairs)
    
    # 2. Plot
    plot_effective_connectivity(results, output_dir=output_dir)
    
    log.progress("Analysis f020 complete.")

if __name__ == "__main__":
    run_f020()
