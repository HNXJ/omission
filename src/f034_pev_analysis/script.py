# core
import os
import numpy as np
from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def compute_omega_sq(data_list, labels):
    """
    Computes Omega-squared PEV.
    """
    if not data_list: return np.zeros(1)
    
    # Concatenate all trials
    all_data = np.concatenate(data_list, axis=0) # (total_trials, time)
    n_trials, n_time = all_data.shape
    unique_labels = np.unique(labels)
    n_groups = len(unique_labels)
    
    pev_time = []
    for t in range(n_time):
        y = all_data[:, t]
        ss_total = np.var(y) * n_trials
        
        ss_between = 0
        for label in unique_labels:
            group_data = y[labels == label]
            if len(group_data) > 0:
                ss_between += len(group_data) * (np.mean(group_data) - np.mean(y))**2
            
        ms_between = ss_between / (n_groups - 1) if n_groups > 1 else 0
        ss_error = ss_total - ss_between
        ms_error = ss_error / (n_trials - n_groups) if (n_trials - n_groups) > 0 else 0
        
        omega_sq = (ss_between - (n_groups - 1) * ms_error) / (ss_total + ms_error + 1e-12)
        pev_time.append(max(0, omega_sq))
        
    return np.array(pev_time)

def run_f034():
    log.action("Starting f034: Percent Explained Variance (Omega-Squared)...")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f034_pev_analysis")
    
    # Compare AAAB vs BBBA in V1
    conds = ["AAAB", "BBBA"]
    area = "V1"
    
    area_data = {}
    for idx, cond in enumerate(conds):
        spk_list = loader.get_signal(mode="spk", area=area, condition=cond, align_to="p1")
        if spk_list:
            # Aggregate across all sessions for this area
            all_trials = []
            for s in spk_list:
                # s shape (trials, units, time)
                pop_rate = np.mean(s, axis=1) * 1000.0 # (trials, time)
                all_trials.append(pop_rate)
            if all_trials:
                area_data[cond] = np.concatenate(all_trials, axis=0)

    if len(area_data) == 2:
        data_list = [area_data["AAAB"], area_data["BBBA"]]
        labels = np.concatenate([np.zeros(len(area_data["AAAB"])), np.ones(len(area_data["BBBA"]))])
        pev = compute_omega_sq(data_list, labels)
        
        # Plotting
        plotter = OmissionPlotter(
            title="Figure f034: Stimulus Identity Fidelity (PEV)",
            x_label="Time",
            y_label="Omega-Squared (PEV)",
            subtitle="Explained variance for A vs B identity in V1.",
            x_unit="ms",
            y_unit="a.u."
        )
        times = np.linspace(-1000, 3000, len(pev))
        plotter.add_trace(go.Scatter(x=times, y=pev, name="V1 Identity PEV", line=dict(color="#CFB87C", width=3)), "PEV")
        
        plotter.add_xline(0, "P1 Onset")
        plotter.add_xline(1000, "P2 Onset")
        plotter.save(str(output_dir), "fig34_pev_analysis")
        
    log.progress("Analysis f034 complete.")

if __name__ == "__main__":
    import plotly.graph_objects as go
    run_f034()
