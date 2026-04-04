
import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

CHECKPOINT_DIR = "D:/Analysis/Omission/local-workspace/checkpoints"
FIGURES_DIR = "D:/Analysis/Omission/local-workspace/figures/coordination"

if not os.path.exists(FIGURES_DIR):
    os.makedirs(FIGURES_DIR)

# Aesthetic Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"

def plot_ppc_summary():
    with open(os.path.join(CHECKPOINT_DIR, "spike_lfp_coordination_results.json"), 'r') as f:
        data = json.load(f)
        
    # Plot Gamma PPC for Omission neurons in V1 and PFC
    fig = make_subplots(rows=1, cols=2, subplot_titles=["V1 Omission Neurons", "PFC Omission Neurons"])
    
    # Omission Category keys: Area_Category_Condition_Band
    for i, area in enumerate(["V1", "PFC"]):
        key_std = f"{area}_Omit-Pref_RRRR_gamma"
        key_omit = f"{area}_Omit-Pref_AAAX_gamma"
        
        if key_std in data:
            fig.add_trace(go.Scatter(x=data[key_std]['time_bins'], y=data[key_std]['mean'], name=f"{area} Std", line=dict(color=GOLD)), row=1, col=i+1)
        if key_omit in data:
            fig.add_trace(go.Scatter(x=data[key_omit]['time_bins'], y=data[key_omit]['mean'], name=f"{area} Omit", line=dict(color=VIOLET)), row=1, col=i+1)
            
        fig.add_vline(x=3093, line_dash="dash", line_color="white", row=1, col=i+1) # Omission onset

    fig.update_layout(title="Spike-LFP PPC (Gamma Band) for Omission Neurons", template="plotly_dark")
    fig.write_html(os.path.join(FIGURES_DIR, "spike_lfp_ppc_gamma.html"))

def plot_ccg_summary():
    with open(os.path.join(CHECKPOINT_DIR, "v1_pfc_ccg_results.json"), 'r') as f:
        data = json.load(f)
        
    # Aggregate CCGs across sessions
    ccg_std_all = []
    ccg_omit_all = []
    
    for ses in data:
        if 'RRRR' in data[ses]: ccg_std_all.append(data[ses]['RRRR'])
        if 'AAAX' in data[ses]: ccg_omit_all.append(data[ses]['AAAX'])
        
    lags = np.arange(-100, 101)
    
    fig = go.Figure()
    if ccg_std_all:
        fig.add_trace(go.Scatter(x=lags, y=np.mean(ccg_std_all, axis=0), name="Standard (RRRR)", line=dict(color=GOLD)))
    if ccg_omit_all:
        fig.add_trace(go.Scatter(x=lags, y=np.mean(ccg_omit_all, axis=0), name="Omission (AAAX)", line=dict(color=VIOLET)))
        
    fig.update_layout(title="V1-PFC Spike-Spike CCG", xaxis_title="Lag (ms)", yaxis_title="Correlation", template="plotly_dark")
    fig.write_html(os.path.join(FIGURES_DIR, "v1_pfc_ccg.html"))

def main():
    plot_ppc_summary()
    plot_ccg_summary()
    print(f"Coordination plots generated in {FIGURES_DIR}")

if __name__ == "__main__":
    main()
