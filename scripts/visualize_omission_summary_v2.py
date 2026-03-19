"""
visualize_omission_summary_v2.py: Final multi-panel summary of omission signaling.
Includes Layer Distribution, Response Strength, LFP PEV, and Onset Latency.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Paths
LAYERED_UNITS_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_layered_v3.csv'
PEV_PATH = r'D:\Analysis\Omission\local-workspace\LFP_Extractions\omission_lfp_pev_v2.npz'
LATENCY_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\omission_latencies_v2.csv'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_units = pd.read_csv(LAYERED_UNITS_PATH)
    df_lat = pd.read_csv(LATENCY_PATH) if os.path.exists(LATENCY_PATH) else None
    
    # 1. Layer Distribution per Area
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    order = ['PFC', 'FEF', 'MT/MST', 'V4/TEO', 'V3/V4', 'V1/V2']
    df_known = df_units[df_units['layer'] != 'unknown']
    
    unique_areas = [o for o in order if o in df_known['area'].unique()]
    layers = ['Superficial', 'L4', 'Deep']
    x = np.arange(len(unique_areas))
    width = 0.2
    
    for i, layer in enumerate(layers):
        counts = [len(df_known[(df_known['area'] == a) & (df_known['layer'] == layer)]) for a in unique_areas]
        ax1.bar(x + (i-1)*width, counts, width, label=layer)
        
    ax1.set_xticks(x)
    ax1.set_xticklabels(unique_areas)
    ax1.set_title("Real Omission Neuron Distribution by Cortical Layer")
    ax1.set_ylabel("Count of Units")
    ax1.legend()
    ax1.grid(True, axis='y', alpha=0.3)
    fig1.savefig(os.path.join(OUTPUT_DIR, 'final_omission_layer_distribution.png'))

    # 2. Omission Strength (Ratio) by Area and Layer
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    for i, area in enumerate(unique_areas):
        for j, layer in enumerate(layers):
            data = df_known[(df_known['area'] == area) & (df_known['layer'] == layer)]['r_fix']
            if not data.empty:
                ax2.boxplot(data, positions=[i + (j-1)*width], widths=width, showfliers=False)
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(unique_areas)
    ax2.set_yscale('log')
    ax2.set_title("Omission Response Strength (Omit/Fix Ratio)")
    ax2.set_ylabel("Ratio (Log Scale)")
    ax2.grid(True, axis='y', alpha=0.3)
    fig2.savefig(os.path.join(OUTPUT_DIR, 'final_omission_strength_by_layer.png'))

    # 3. LFP PEV Heatmaps (Sample areas)
    if os.path.exists(PEV_PATH):
        pev_data = np.load(PEV_PATH)
        # Select best probe for PFC and V1
        keys = pev_data.files
        pfc_keys = [k for k in keys if 'PFC' in k or '230901_p0' in k] # Session 230901 P0 is PFC
        v1_keys = [k for k in keys if 'V1' in k or '230720_p0' in k]
        
        plot_keys = []
        if pfc_keys: plot_keys.append(pfc_keys[0])
        if v1_keys: plot_keys.append(v1_keys[0])
        
        if plot_keys:
            fig3, axes = plt.subplots(len(plot_keys), 1, figsize=(10, 4*len(plot_keys)))
            if len(plot_keys) == 1: axes = [axes]
            for i, k in enumerate(plot_keys):
                im = axes[i].imshow(pev_data[k], aspect='auto', cmap='magma', extent=[0, 1000, 127, 0])
                axes[i].set_title(f"LFP PEV (Omission Onset at 0ms): {k}")
                axes[i].set_ylabel("Channel (Depth)")
                plt.colorbar(im, ax=axes[i], label='PEV')
            axes[-1].set_xlabel("Time after Omission (ms)")
            fig3.tight_layout()
            fig3.savefig(os.path.join(OUTPUT_DIR, 'final_omission_lfp_pev_heatmaps.png'))

    # 4. Latency Hierarchy Plot
    if df_lat is not None and not df_lat.empty:
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        # Filter valid latencies
        df_valid_lat = df_lat.dropna(subset=['latency_ms'])
        if not df_valid_lat.empty:
            for i, area in enumerate(unique_areas):
                data = df_valid_lat[df_valid_lat['area'] == area]['latency_ms']
                if not data.empty:
                    ax4.scatter([i]*len(data) + np.random.normal(0, 0.1, len(data)), data, alpha=0.6)
                    ax4.plot([i-0.2, i+0.2], [np.median(data), np.median(data)], 'k-', lw=2)
            
            ax4.set_xticks(x)
            ax4.set_xticklabels(unique_areas)
            ax4.set_ylabel("Onset Latency (ms after p4)")
            ax4.set_title("Omission Onset Hierarchy (Spiking)")
            ax4.grid(True, alpha=0.3)
            fig4.savefig(os.path.join(OUTPUT_DIR, 'final_omission_latency_hierarchy.png'))

    print(f"Final summary visualizations saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
