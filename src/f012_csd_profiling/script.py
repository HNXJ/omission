from src.analysis.io.logger import log
from src.f012_csd_profiling.analysis import run_f012_analysis
from src.f012_csd_profiling.plot import plot_mi_matrix
from pathlib import Path
import os

def run_f012():
    log.progress("Starting Analysis f012: Current Source Density (CSD) Profiling")
    output_dir = Path("D:/drive/outputs/oglo-8figs/f012-csd-profiling")
    os.makedirs(output_dir, exist_ok=True)
    
    results = run_f012_analysis()
    if results:
        plot_mi_matrix(results, output_dir=str(output_dir))
    log.progress("Analysis f012 complete.")

if __name__ == "__main__":
    run_f012()