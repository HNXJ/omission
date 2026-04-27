# core
import os
import numpy as np
from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def run_f035():
    log.action("Starting f035: Deviance-Scaling Response Analysis...")
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f035-deviance-scaling")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area = "V1"
    conds = ["AXAB", "AXBB"] # Frequent vs Rare omission? 
    # Or AXAB vs RXRR (Random)?
    # Let's use AXAB (Frequent) vs AXBB (Rare/Novel?)
    # The plan says "Rare vs Frequent omissions".
    
    responses = {}
    for cond in conds:
        spk_list = loader.get_signal(mode="spk", area=area, condition=cond, align_to="omission")
        if not spk_list: continue
        # Average across trials, units, and sessions
        ts = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in spk_list], axis=0), axis=0)
        responses[cond] = ts
        
    # Plotting
    plotter = OmissionPlotter(title="Figure f035: Deviance Scaling (Surprise Magnitude)", template="plotly_dark")
    times = np.linspace(-1000, 1000, 2000)
    for cond, ts in responses.items():
        name = "Frequent Omission" if cond == "AXAB" else "Rare Omission"
        color = "#CFB87C" if cond == "AXAB" else "#9400D3"
        plotter.add_trace(go.Scatter(x=times, y=ts, name=name, line=dict(color=color)), cond)
        
    plotter.set_axes("Time (ms)", "", "Firing Rate (Hz)", "")
    plotter.add_xline(0, "Omission", color="white", dash="dash")
    plotter.save(str(output_dir), "f035_deviance_scaling")

if __name__ == "__main__":
    import plotly.graph_objects as go
    run_deviance_scaling()
