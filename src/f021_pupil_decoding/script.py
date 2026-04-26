from pathlib import Path
# beta
from src.analysis.io.loader import DataLoader
import os
import numpy as np
from src.analysis.io.logger import log
from src.f021_pupil_decoding.analysis import analyze_pupil_surprise
from src.f021_pupil_decoding.plot import plot_pupil_surprise

def run_f021():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f021_pupil_decoding")
    """
    Main execution entry for Figure 21.
    """
    log.progress("Starting Analysis f021: Pupil Decoding")
    
    # Define sessions to analyze
    sessions = loader.get_sessions()[:5] # Grab up to 5 available sessions
    
    # 1. Run Analysis
    results = analyze_pupil_surprise(loader, sessions)
    
    # 2. Plot
    if results:
        # Override to match user requested path
        custom_out = loader.get_output_dir("f021_pupil_surprise")
        plot_pupil_surprise(results, output_dir=str(custom_out))
    
    log.progress("Analysis f021 complete.")

if __name__ == "__main__":
    run_f021()
