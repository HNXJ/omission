from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f046_state_space_trajectories.analysis import analyze_state_space
from src.f046_state_space_trajectories.plot import plot_trajectories
import os

def run_f046():
    loader = DataLoader()
    
    # Adhere strictly to the requested folder mandate (max 49 chars, no underscores)
    output_dir = Path(r"D:\drive\outputs\oglo-8figs\f046-state-space-trajectories")
    os.makedirs(output_dir, exist_ok=True)
    
    log.progress("Starting Analysis f046: High-Dimensional State-Space Trajectories")
    
    areas = list(loader.area_map.keys())
    
    # 1. Run Analysis
    results = analyze_state_space(areas)
    
    # 2. Plot
    if results:
        plot_trajectories(results, output_dir=str(output_dir))
    
    log.progress("Analysis f046 complete.")

if __name__ == "__main__":
    run_f046()