"""
visualize_omission_summary.py: Generates multi-panel plots for omission neurons across layers and brain areas.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

LAYERED_UNITS_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_layered.csv'
PEV_PATH = r'D:\Analysis\Omission\local-workspace\LFP_Extractions\omission_lfp_pev.npz'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(LAYERED_UNITS_PATH): return
    df = pd.read_csv(LAYERED_UNITS_PATH)
    
    # Filter for "Real" - ensure ratio is high enough
    # User said "Real" omission neurons only fire for omission.
    # So r_fix and r_seq should both be > 2.0 ideally.
    df = df[(df['r_fix'] > 2.0) & (df['r_seq'] > 2.0)]
    
    # 1. Layer Distribution per Area
    plt.figure(figsize=(12, 6))
    order = ['PFC', 'FEF', 'MT', 'V4', 'V3/V4', 'V1/V2']
    df_known = df[df['layer'] != 'unknown']
    
    unique_areas = [o for o in order if o in df_known['area'].unique()]
    layers = ['Superficial', 'L4', 'Deep']
    x = np.arange(len(unique_areas))
    width = 0.2
    
    for i, layer in enumerate(layers):
        counts = [len(df_known[(df_known['area'] == a) & (df_known['layer'] == layer)]) for a in unique_areas]
        plt.bar(x + (i-1)*width, counts, width, label=layer)
        
    plt.xticks(x, unique_areas)
    plt.title("Real Omission Neuron Distribution (Strict: r_fix > 2, r_seq > 2)")
    plt.ylabel("Count of Units")
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.savefig(os.path.join(OUTPUT_DIR, 'real_omission_layer_distribution.png'))
    plt.close()

    # 3. Omission Index (Ratio) by Area and Layer
    plt.figure(figsize=(12, 6))
    for i, area in enumerate(unique_areas):
        for j, layer in enumerate(layers):
            data = df_known[(df_known['area'] == area) & (df_known['layer'] == layer)]['r_fix']
            if not data.empty:
                plt.boxplot(data, positions=[i + (j-1)*width], widths=width, showfliers=False)
    
    plt.xticks(np.arange(len(unique_areas)), unique_areas)
    plt.yscale('log')
    plt.title("Omission Response Strength (Omit/Fix Ratio)")
    plt.ylabel("Ratio (Log Scale)")
    plt.grid(True, axis='y', alpha=0.3)
    plt.savefig(os.path.join(OUTPUT_DIR, 'real_omission_strength_by_layer.png'))
    plt.close()

    print(f"Summary visualizations saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
