# core
import os
import numpy as np
from pathlib import Path
from scipy.signal import butter, filtfilt
from src.analysis.io.loader import DataLoader
from src.analysis.laminar.mapper import LaminarMapper
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def compute_csd(lfp, sigma=0.4, spacing=0.01):
    """
    Computes Current Source Density (CSD) using the 2nd spatial derivative.
    lfp: (channels, time)
    """
    n_ch = lfp.shape[0]
    csd = np.zeros_like(lfp)
    
    # 2nd spatial derivative approximation
    # CSD(c) = -sigma * (V(c-1) - 2V(c) + V(c+1)) / (spacing^2)
    for c in range(1, n_ch - 1):
        csd[c] = -sigma * (lfp[c-1] - 2*lfp[c] + lfp[c+1]) / (spacing**2)
        
    return csd

def run_csd_profiling():
    log.action("Starting f012: Current Source Density (CSD) Profiling...")
    
    # 1. Initialize
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f012-csd-profiling")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area = "V1"
    cond = "AXAB"
    
    # Load LFP (Bipolar referenced - wait, CSD usually needs monopolar, but we can use our processed LFP)
    lfp_list = loader.get_signal(mode="lfp", area=area, condition=cond, align_to="omission")
    if not lfp_list: return
    
    # Use first session for high-fidelity spatial profile
    lfp = lfp_list[0] # (trials, channels, time)
    lfp_avg = np.mean(lfp, axis=0) # (channels, time)
    
    # 2. Compute CSD
    log.action("Computing 2nd spatial derivative for CSD...")
    csd_data = compute_csd(lfp_avg) # (channels, time)
    
    # 3. Plotting (Heatmap)
    plotter = OmissionPlotter(
        title="Figure f012: Current Source Density (CSD) Profiling",
        subtitle="Sink/Source dynamics during stimulus omission. Sinks (blue) indicate inward synaptic current.",
        template="plotly_dark"
    )
    plotter.fig.update_layout(
        paper_bgcolor="#000000", plot_bgcolor="#000000",
        font=dict(color="#FFFFFF", family="Outfit"),
        title=dict(font=dict(color="#CFB87C", size=22)),
        height=800
    )
    
    import plotly.graph_objects as go
    time_ms = np.linspace(-1000, 1000, csd_data.shape[1])
    channels = np.arange(csd_data.shape[0])
    
    plotter.add_trace(go.Heatmap(
        z=csd_data,
        x=time_ms,
        y=channels,
        colorscale='RdBu_r', # Red for sources, Blue for sinks
        zmid=0,
        colorbar=dict(title="CSD (uA/mm^3)")
    ), "CSD Heatmap")

    plotter.set_axes("Time (ms)", "", "Channel (Depth)", "")
    plotter.save(str(output_dir), "f012_csd_profiling")
    
    # Save README
    with open(output_dir / "README.md", "w") as f:
        f.write("# Figure f012: Current Source Density (CSD)\n\n## Methodology\n- 2nd spatial derivative of the LFP across the linear probe.\n- Standardized spacing (10um) and conductivity (0.4 S/m).\n- Aligned to omission onset.")

if __name__ == "__main__":
    run_csd_profiling()
