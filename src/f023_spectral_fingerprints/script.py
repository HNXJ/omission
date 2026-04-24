from pathlib import Path
# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f023_spectral_fingerprints.analysis import analyze_spectral_fingerprints
from src.f023_spectral_fingerprints.plot import plot_spectral_fingerprints

def run_f023():
    """
    Main execution entry for Figure 23.
    """
    log.progress("Starting Analysis f023: Spectral Fingerprints")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f023-spectral-fingerprints")
    
    # Define sessions and areas to analyze
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    # 1. Run Analysis
    freqs, results = analyze_spectral_fingerprints(loader, sessions, areas)
    
    # 2. Plot
    if results:
        plot_spectral_fingerprints(freqs, results, output_dir=output_dir)
    
    log.progress("Analysis f023 complete.")

if __name__ == "__main__":
    run_f023()
