from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f010_sfc_delta.analysis import analyze_sfc_delta
from src.f010_sfc_delta.plot import plot_sfc_delta
from pathlib import Path
import os

def run_f010():
    log.progress("Starting Analysis f010: Continuous Delta SFC")
    output_dir = Path("D:/drive/outputs/oglo-8figs/f010-sfc-delta")
    os.makedirs(output_dir, exist_ok=True)
    
    results = analyze_sfc_delta()
    if results:
        plot_sfc_delta(results, output_dir=str(output_dir))
    log.progress("Analysis f010 complete.")

if __name__ == "__main__":
    run_f010()