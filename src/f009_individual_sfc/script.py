from pathlib import Path
import os
from src.analysis.io.logger import log
from src.f009_individual_sfc.analysis import analyze_individual_sfc
from src.f009_individual_sfc.plot import plot_individual_sfc

def run_f009():
    log.progress("Starting Analysis f009: Phase Consistency and Circular Distributions")
    
    # Target directory matching 49-char limit and no-underscore policy
    output_dir = Path(r"D:\drive\outputs\oglo-8figs\f009-individual-sfc")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Run Analysis
    results = analyze_individual_sfc()
    
    # 2. Plot
    if results:
        plot_individual_sfc(results, output_dir=str(output_dir))
        
    log.progress("Analysis f009 complete.")

if __name__ == "__main__":
    run_f009()