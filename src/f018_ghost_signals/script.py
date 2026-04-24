from pathlib import Path
# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f018_ghost_signals.analysis import analyze_ghost_signals
from src.f018_ghost_signals.plot import plot_ghost_signals

def run_f018():
    """
    Main execution entry for Figure 18.
    """
    log.progress("Starting Analysis f018: Ghost Signals")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f018-ghost-signals")
    
    # Define sessions and areas to analyze
    sessions = loader.get_sessions() # Process all sessions for maximum yield
    areas = ["V1", "V4", "PFC", "FEF"]
    
    # 1. Run Analysis
    results = analyze_ghost_signals(loader, sessions, areas)
    
    # 2. Plot
    plot_ghost_signals(results, output_dir=output_dir)
    
    log.progress("Analysis f018 complete.")

if __name__ == "__main__":
    run_f018()
