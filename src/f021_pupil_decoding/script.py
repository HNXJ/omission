# beta
import os
import numpy as np
from src.analysis.io.logger import log
from src.f021_pupil_decoding.analysis import analyze_pupil_surprise
from src.f021_pupil_decoding.plot import plot_pupil_surprise

def run_f021():
    """
    Main execution entry for Figure 21.
    """
    log.progress("Starting Analysis f021: Pupil Decoding")
    
    # Define sessions to analyze
    sessions = ["230629", "230630", "230714", "230719"]
    
    # 1. Run Analysis
    results = analyze_pupil_surprise(sessions)
    
    # 2. Plot
    if results:
        plot_pupil_surprise(results)
    
    log.progress("Analysis f021 complete.")

if __name__ == "__main__":
    run_f021()
