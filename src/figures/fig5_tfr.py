# core
import numpy as np
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
from src.analysis.io.loader import DataLoader
from src.analysis.lfp.signal import _process_lfp

from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.visualization.lfp_plotting import create_tfr_figure

def generate_figure_5(output_dir: str = "D:/drive/outputs/oglo-8figs/f005"):
    """
    Generates Figure 5: Omission TFR (Time-Frequency Representation).
    Standardizes on Omission-Local alignment and linear power.
    """
    log.progress(f"""[action] Generating Figure 5: Omission TFR (11 Areas) in {output_dir}...""")
    
    loader = DataLoader()
    
    for area in loader.CANONICAL_AREAS:
        # 1. Run unified pipeline
        results = run_lfp_spectral_pipeline(area, "AXAB")
        if not results: continue
            
        # 2. Call unified plotting
        plotter = create_tfr_figure(
            freqs=results["freqs"], 
            times_ms=results["times"], 
            power=results["tfr"], 
            title=f"Figure 5: {area} Omission TFR",
            area=area
        )
        
        plotter.save(output_dir, f"fig5_tfr_local_{area}")
        
    log.progress(f"""[action] Figure 5 complete.""")

if __name__ == "__main__":
    generate_figure_5()