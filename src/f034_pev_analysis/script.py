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
    data_list: list of (trials, time)
    labels: list of trial labels
    """
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
            ss_between += len(group_data) * (np.mean(group_data) - np.mean(y))**2
            
        ms_between = ss_between / (n_groups - 1)
        ss_error = ss_total - ss_between
        ms_error = ss_error / (n_trials - n_groups)
        
        omega_sq = (ss_between - (n_groups - 1) * ms_error) / (ss_total + ms_error + 1e-12)
        pev_time.append(max(0, omega_sq))
        
    return np.array(pev_time)

def run_pev_analysis():
    log.action("Starting f034: Percent Explained Variance (Omega-Squared)...")
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f034-pev-analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area = "V1"
    # Compare AXAB vs AXBB (Stimulus Identity during omission?)
    # Or identity of the PRECEDING stimulus.
    # The plan says "stimulus identity information fidelity". 
    # Let's compare responses to A vs B in a standard stimulus period.
    
    conds = ["AAAB", "BBAB"] # Identity of first stim?
    
    # Load spiking data for Superficial and Deep
    # We'll use the mapper to stratify
    from src.analysis.laminar.mapper import LaminarMapper
    mapper = LaminarMapper()
    
    pev_layers = {}
    for layer_name, depth_range in [("Superficial", (0, 40)), ("Deep", (70, 128))]:
        layer_data = []
        layer_labels = []
        
        for idx, cond in enumerate(conds):
            spk_list = loader.get_signal(mode="spk", area=area, condition=cond, align_to="p1")
            if not spk_list: continue
            
            for s_idx, s in enumerate(spk_list):
                # Filter units by depth
                session_name = loader.sessions[s_idx]
                depths = mapper.get_depths(session_name, area)
                mask = (depths >= depth_range[0]) & (depths < depth_range[1])
                if not np.any(mask): continue
                
                # Average across valid units
                pop_rate = np.mean(s[:, mask, :], axis=1) # (trials, time)
                layer_data.append(pop_rate)
                layer_labels.extend([idx] * pop_rate.shape[0])
                
        if layer_data:
            pev_layers[layer_name] = compute_omega_sq(layer_data, np.array(layer_labels))
            
    # Plotting
    plotter = OmissionPlotter(title="Figure f034: Information Fidelity (PEV)", template="plotly_dark")
    times = np.linspace(-1000, 1000, 2000)
    for layer, pev in pev_layers.items():
        color = "#CFB87C" if layer == "Superficial" else "#9400D3"
        plotter.add_trace(go.Scatter(x=times, y=pev, name=layer, line=dict(color=color)), layer)
        
    plotter.set_axes("Time (ms)", "", "Omega-Squared (PEV)", "")
    plotter.add_xline(0, "P1 Onset", color="white", dash="dash")
    plotter.save(str(output_dir), "f034_pev_analysis")

if __name__ == "__main__":
    import plotly.graph_objects as go
    run_pev_analysis()
