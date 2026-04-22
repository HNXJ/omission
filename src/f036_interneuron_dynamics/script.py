# core
import os
import numpy as np
from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import plotly.graph_objects as go

def run_interneuron_dynamics():
    log.action("Starting f036: Inhibitory Interneuron Dynamics...")
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f036-interneuron-dynamics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area = "V1"
    cond = "AXAB"
    
    spk_list = loader.get_signal(mode="spk", area=area, condition=cond, align_to="omission")
    if not spk_list: return
    
    responses = {"Interneurons": [], "Principal": []}
    
    for s_idx, s in enumerate(spk_list):
        # Placeholder: units with mean rate > 15Hz are "Interneurons"
        mean_rates = np.mean(s, axis=(0, 2)) * 1000 # Hz
        is_fs = mean_rates > 15
        
        fs_pop = np.mean(s[:, is_fs, :], axis=(0, 1)) if np.any(is_fs) else np.zeros(s.shape[-1])
        rs_pop = np.mean(s[:, ~is_fs, :], axis=(0, 1)) if np.any(~is_fs) else np.zeros(s.shape[-1])
        
        responses["Interneurons"].append(fs_pop)
        responses["Principal"].append(rs_pop)
        
    ts_fs = np.mean(np.stack(responses["Interneurons"]), axis=0)
    ts_rs = np.mean(np.stack(responses["Principal"]), axis=0)
    
    # Plotting
    plotter = OmissionPlotter(title="Figure f036: Inhibitory Interneuron Dynamics", template="plotly_dark")
    times = np.linspace(-1000, 1000, len(ts_fs))
    
    plotter.add_trace(go.Scatter(x=times, y=ts_fs, name="Interneurons (FS)", line=dict(color="#CFB87C")), "Interneurons")
    plotter.add_trace(go.Scatter(x=times, y=ts_rs, name="Principal (RS)", line=dict(color="#9400D3")), "Principal")
    
    plotter.set_axes("Time (ms)", "", "Firing Rate (Hz)", "")
    plotter.add_xline(0, "Omission", color="white", dash="dash")
    plotter.save(str(output_dir), "f036_interneuron_dynamics")

if __name__ == "__main__":
    run_interneuron_dynamics()
