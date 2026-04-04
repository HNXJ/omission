
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

RESULTS_FILE = "D:/Analysis/Omission/local-workspace/checkpoints/variability_quenching_results.json"
FIGURES_DIR = "D:/Analysis/Omission/local-workspace/figures/variability"

if not os.path.exists(FIGURES_DIR):
    os.makedirs(FIGURES_DIR)

# Aesthetic Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"
WHITE = "#FFFFFF"

# Area Ordering
HIERARCHY = ["V1", "V2", "V3", "V3d", "V3a", "V4", "MT", "MST", "TEO", "FST", "FEF", "PFC"]

def aggregate_traces(results_dict, key_filter):
    """
    Aggregates session-level traces into a single mean + sem trace.
    """
    all_traces = []
    time_bins = None
    
    for key in results_dict:
        if key_filter in key:
            for entry in results_dict[key]:
                if 'fano' in entry:
                    all_traces.append(entry['fano'])
                    time_bins = entry['time_bins']
                elif 'variance' in entry:
                    all_traces.append(entry['variance'])
                    time_bins = np.arange(len(entry['variance'])) # Assume samples
                    
    if len(all_traces) == 0:
        return None, None, None
        
    all_traces = np.array([t for t in all_traces if len(t) == len(all_traces[0])])
    mean_trace = np.nanmean(all_traces, axis=0)
    sem_trace = np.nanstd(all_traces, axis=0) / np.sqrt(np.sum(~np.isnan(all_traces), axis=0))
    
    return time_bins, mean_trace, sem_trace

def plot_area_comparison(data, modality='spk'):
    """
    Plots Standard vs Omission for each area.
    """
    results = data['spk_mmff'] if modality == 'spk' else data['lfp_variance']
    metric_name = "MMFF" if modality == 'spk' else "LFP Variance"
    
    # Identify unique areas in results
    areas = sorted(list(set([k.split('_')[0] for k in results.keys()])))
    
    fig = make_subplots(rows=(len(areas)+1)//2, cols=2, subplot_titles=areas)
    
    for i, area in enumerate(areas):
        row = i // 2 + 1
        col = i % 2 + 1
        
        # Standard (RRRR)
        t_std, m_std, s_std = aggregate_traces(results, f"{area}_RRRR")
        # Omission (RRRX - Omit p4)
        t_omit, m_omit, s_omit = aggregate_traces(results, f"{area}_RRRX")
        
        if t_std is not None:
            fig.add_trace(go.Scatter(x=t_std, y=m_std, name=f"{area} Std", line=dict(color=GOLD)), row=row, col=col)
            # Add error bands
            fig.add_trace(go.Scatter(x=np.concatenate([t_std, t_std[::-1]]), 
                                     y=np.concatenate([m_std+s_std, (m_std-s_std)[::-1]]),
                                     fill='toself', fillcolor=GOLD, opacity=0.2, line=dict(color='rgba(255,255,255,0)'), showlegend=False), row=row, col=col)
        
        if t_omit is not None:
            fig.add_trace(go.Scatter(x=t_omit, y=m_omit, name=f"{area} Omit", line=dict(color=VIOLET)), row=row, col=col)
            fig.add_trace(go.Scatter(x=np.concatenate([t_omit, t_omit[::-1]]), 
                                     y=np.concatenate([m_omit+s_omit, (m_omit-s_omit)[::-1]]),
                                     fill='toself', fillcolor=VIOLET, opacity=0.2, line=dict(color='rgba(255,255,255,0)'), showlegend=False), row=row, col=col)
        
        # Add vertical lines for stimulus timings
        # Stim 1: 0, Stim 2: 1031, Stim 3: 2062, Stim 4/Omit: 3093
        for onset in [0, 1031, 2062, 3093]:
            fig.add_vline(x=onset, line_dash="dash", line_color="gray", row=row, col=col)

    fig.update_layout(height=300 * ((len(areas)+1)//2), width=1000, title=f"Neural Variability Quenching ({metric_name})", template="plotly_dark")
    fig.write_html(os.path.join(FIGURES_DIR, f"{modality}_quenching_comparison.html"))

def plot_quenching_hierarchy(data):
    """
    Bar plot of quenching magnitude across the hierarchy.
    """
    results = data['spk_mmff']
    areas = HIERARCHY
    
    quenching_mags = []
    area_labels = []
    
    for area in areas:
        # Standard (RRRR)
        t, m, s = aggregate_traces(results, f"{area}_RRRR")
        if t is not None:
            # Baseline: -500 to 0 (Time bins are centered)
            baseline_mask = (np.array(t) > -500) & (np.array(t) < 0)
            baseline_val = np.nanmean(m[baseline_mask])
            
            # Post-stim: 0 to 4000
            post_mask = (np.array(t) > 0) & (np.array(t) < 4000)
            quenching = np.nanmin(m[post_mask]) - baseline_val
            
            quenching_mags.append(quenching)
            area_labels.append(area)
            
    fig = go.Figure(go.Bar(x=area_labels, y=quenching_mags, marker_color=VIOLET))
    fig.update_layout(title="Max MMFF Quenching Across Hierarchy", yaxis_title="ΔFano Factor", template="plotly_dark")
    fig.write_html(os.path.join(FIGURES_DIR, "mmff_quenching_hierarchy.html"))

def main():
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)
        
    plot_area_comparison(data, modality='spk')
    plot_area_comparison(data, modality='lfp')
    plot_quenching_hierarchy(data)
    
    print(f"Figures generated in {FIGURES_DIR}")

if __name__ == "__main__":
    main()
