# core
import os
import numpy as np
from pathlib import Path
from scipy.signal import welch
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def run_rhythmic_evolution():
    log.action("Starting f013: Trial-by-Trial Rhythmic Evolution...")
    
    # 1. Initialize
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f013-rhythmic-evolution")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area = "V1"
    cond = "AAAB" # Use a predictable sequence to see adaptation
    
    lfp_list = loader.get_signal(mode="lfp", area=area, condition=cond, align_to="p1")
    if not lfp_list: return
    
    # Average channels per session first to handle varying channel counts
    session_avgs = [np.mean(ses_lfp, axis=1) for ses_lfp in lfp_list] # List of (trials, time)
    lfp_avg = np.concatenate(session_avgs, axis=0) # (total_trials, time)
    
    n_trials = lfp_avg.shape[0]
    gamma_pwr = []
    beta_pwr = []
    
    # 2. Compute power across trials
    for t in range(n_trials):
        f, psd = welch(lfp_avg[t], fs=1000, nperseg=256)
        
        gamma_mask = (f >= 30) & (f <= 80)
        beta_mask = (f >= 15) & (f <= 30)
        
        gamma_pwr.append(np.mean(psd[gamma_mask]))
        beta_pwr.append(np.mean(psd[beta_mask]))
        
    gamma_pwr = np.array(gamma_pwr)
    beta_pwr = np.array(beta_pwr)
    
    # Normalize
    gamma_pwr /= (np.mean(gamma_pwr) + 1e-12)
    beta_pwr /= (np.mean(beta_pwr) + 1e-12)
    
    # 3. Plotting
    plotter = OmissionPlotter(
        title="Figure f013: Trial-by-Trial Rhythmic Evolution",
        subtitle="Tracking Gamma vs. Beta power adaptation during predictable sequences.",
        template="plotly_white"
    )
    # Mandate: White background, black axis
    plotter.fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(color="#000000", family="Arial"),
        title=dict(font=dict(color="#000000", size=22)),
        height=800
    )
    
    import plotly.graph_objects as go
    trials = np.arange(n_trials)
    
    plotter.add_trace(go.Scatter(x=trials, y=gamma_pwr, name="Gamma (30-80Hz)", line=dict(color="#CFB87C", width=3)), "Gamma")
    plotter.add_trace(go.Scatter(x=trials, y=beta_pwr, name="Beta (15-30Hz)", line=dict(color="#9400D3", width=3)), "Beta")

    plotter.set_axes("Trial Index", "", "Normalized Power", "")
    plotter.save(str(output_dir), "f013_rhythmic_evolution")
    
    # Save README
    with open(output_dir / "README.md", "w") as f:
        f.write("# Figure f013: Rhythmic Evolution\n\n## Methodology\n- Welch PSD calculated per trial for Gamma and Beta bands.\n- Power normalized to mean across trials.\n- Visualizing adaptation/quenching trends.")

if __name__ == "__main__":
    run_rhythmic_evolution()
