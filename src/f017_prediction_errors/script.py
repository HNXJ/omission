from pathlib import Path
# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f017_prediction_errors.analysis import analyze_prediction_errors
from src.f017_prediction_errors.plot import plot_prediction_error_scaling

def run_f017():
    """
    Main execution entry for Figure 17.
    """
    log.progress("Starting Analysis f017: Prediction Error Scaling")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f017_prediction_errors")
    
    # Define sessions and areas to analyze
    # For speed in this turn, let's pick a few key sessions
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    # 1. Run Analysis
    results = analyze_prediction_errors(loader, sessions, areas)
    
    # 2. Plot
    plot_prediction_error_scaling(results, output_dir=output_dir)
    
    log.progress("Analysis f017 complete.")

if __name__ == "__main__":
    run_f017()
