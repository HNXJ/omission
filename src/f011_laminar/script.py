from src.analysis.io.logger import log
from src.f011_laminar.analysis import analyze_laminar_routing
from src.f011_laminar.plot import plot_laminar_routing
from pathlib import Path
import os

def run_f011():
    log.progress("Starting Analysis f011: Laminar Cortical Mapping")
    output_dir = Path("D:/drive/outputs/oglo-8figs/f011-laminar-mapping")
    os.makedirs(output_dir, exist_ok=True)
    
    results = analyze_laminar_routing()
    if results:
        plot_laminar_routing(results, output_dir=str(output_dir))
    log.progress("Analysis f011 complete.")

if __name__ == "__main__":
    run_f011()