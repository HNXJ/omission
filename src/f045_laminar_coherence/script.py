# core
import os
import numpy as np
from pathlib import Path
from scipy.signal import csd, welch
from src.analysis.io.loader import DataLoader
from src.analysis.laminar.mapper import LaminarMapper
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def compute_icoh(sig1, sig2, fs=1000, nperseg=256):
    """
    Computes Imaginary Coherence (iCOH).
    """
    f, sxy = csd(sig1, sig2, fs=fs, nperseg=nperseg, axis=-1)
    _, sxx = welch(sig1, fs=fs, nperseg=nperseg, axis=-1)
    _, syy = welch(sig2, fs=fs, nperseg=nperseg, axis=-1)
    
    # Coherency
    coherency = sxy / np.sqrt(sxx * syy + 1e-12)
    # Imaginary part
    icoh = np.imag(coherency)
    return f, icoh

def run_laminar_coherence():
    log.action("Starting f045: Laminar Functional Connectivity Analysis...")
    
    # 1. Initialize
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f045-laminar-coherence")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    conditions = ["AXAB", "AAAB"]
    target_pairs = [
        ("V1", "PFC"),
    ]
    
    # Canonical boundaries from LaminarMapper
    strata_bounds = {"Superficial": (0, 40), "L4": (40, 70), "Deep": (70, 128)}
    strata_names = ["Superficial", "L4", "Deep"]
    
    results = {f"{p[0]}-{p[1]}": {cond: {} for cond in conditions} for p in target_pairs}
    
    for area1, area2 in target_pairs:
        for cond in conditions:
            log.action(f"Computing iCOH for {area1} <-> {area2} ({cond})...")
            
            lfp1_list = loader.get_signal(mode="lfp", area=area1, condition=cond, align_to="omission")
            lfp2_list = loader.get_signal(mode="lfp", area=area2, condition=cond, align_to="omission")
            
            if not lfp1_list or not lfp2_list: continue
            
            for l1_name in strata_names:
                for l2_name in strata_names:
                    log.action(f"Laminar pair: {l1_name} vs {l2_name}")
                    
                    sig1_trials = []
                    sig2_trials = []
                    
                    # Iterate through sessions
                    for s_idx in range(min(len(lfp1_list), len(lfp2_list))):
                        s1_lfp = lfp1_list[s_idx]
                        s2_lfp = lfp2_list[s_idx]
                        
                        b1_start, b1_end = strata_bounds[l1_name]
                        b2_start, b2_end = strata_bounds[l2_name]
                        
                        l1_idx = np.arange(max(0, b1_start), min(s1_lfp.shape[1], b1_end))
                        l2_idx = np.arange(max(0, b2_start), min(s2_lfp.shape[1], b2_end))
                        
                        if len(l1_idx) and len(l2_idx):
                            sig1_trials.append(np.mean(s1_lfp[:, l1_idx, :], axis=1))
                            sig2_trials.append(np.mean(s2_lfp[:, l2_idx, :], axis=1))
                    
                    if not sig1_trials or not sig2_trials: continue
                    
                    sig1 = np.concatenate(sig1_trials, axis=0)
                    sig2 = np.concatenate(sig2_trials, axis=0)
                    
                    # Compute trial-average iCOH
                    f, icoh_list = [], []
                    for t in range(sig1.shape[0]):
                        f_vals, icoh_vals = compute_icoh(sig1[t], sig2[t])
                        f = f_vals
                        icoh_list.append(icoh_vals)
                    
                    mean_icoh = np.mean(icoh_list, axis=0)
                    results[f"{area1}-{area2}"][cond][f"{l1_name}-{l2_name}"] = {
                        "f": f,
                        "icoh": mean_icoh
                    }

    # 2. Plotting
    plotter = OmissionPlotter(
        title="Figure f045: Laminar Functional Connectivity (iCOH)",
        subtitle="Inter-areal Imaginary Coherence between V1 and PFC layers. Focus on Beta band (15-30Hz).",
        template="plotly_dark"
    )
    plotter.fig.update_layout(
        paper_bgcolor="#000000", plot_bgcolor="#000000",
        font=dict(color="#FFFFFF", family="Outfit"),
        title=dict(font=dict(color="#CFB87C", size=22)),
        height=800
    )
    
    import plotly.graph_objects as go
    for pair_name in results:
        for cond in conditions:
            z_matrix = np.zeros((3, 3))
            for i, l1 in enumerate(strata_names):
                for j, l2 in enumerate(strata_names):
                    key = f"{l1}-{l2}"
                    if key in results[pair_name][cond]:
                        data = results[pair_name][cond][key]
                        beta_mask = (data["f"] >= 15) & (data["f"] <= 30)
                        z_matrix[i, j] = np.mean(np.abs(data["icoh"][beta_mask]))
            
            name = f"{pair_name} - {cond}"
            plotter.add_trace(go.Heatmap(
                z=z_matrix,
                x=strata_names,
                y=strata_names,
                colorscale='Viridis',
                name=name,
                visible=(cond == "AXAB")
            ), name)

    plotter.set_axes("PFC Layers", "", "V1 Layers", "")
    plotter.save(str(output_dir), "f045_laminar_coherence")

if __name__ == "__main__":
    run_laminar_coherence()
