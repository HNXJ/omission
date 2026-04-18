# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f022_dimensionality_reduction.analysis import analyze_pca_trajectories
from src.f022_dimensionality_reduction.plot import plot_pca_trajectories

def run_f022():
    """
    Main execution entry for Figure 22.
    """
    log.progress("Starting Analysis f022: Dimensionality Reduction")
    
    loader = DataLoader()
    
    # Define sessions and area
    sessions = ["230629", "230630"]
    area = "PFC"
    
    # 1. Run Analysis
    results = analyze_pca_trajectories(loader, sessions, area)
    
    # 2. Plot
    if results:
        plot_pca_trajectories(results)
    
    log.progress("Analysis f022 complete.")

if __name__ == "__main__":
    run_f022()
