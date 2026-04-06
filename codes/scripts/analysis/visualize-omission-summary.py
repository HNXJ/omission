"""
visualize_omission_summary.py: Final multi-panel summary of omission signaling.
Includes Layer Distribution, Response Strength, LFP PEV, and Robust Onset Latency.
"""
from codes.config.paths import FIGURES_DIR, PROCESSED_DATA_DIR, PROJECT_ROOT

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Paths
LAYERED_UNITS_PATH = str(PROJECT_ROOT / 'checkpoints
eal_omission_units_layered_v3.csv')
PEV_PATH = str(PROJECT_ROOT / 'LFP_Extractions/omission_lfp_pev_v2.npz')
LATENCY_PATH = str(PROCESSED_DATA_DIR / 'area_population_latencies.csv')
OUTPUT_DIR = str(FIGURES_DIR)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_units = pd.read_csv(LAYERED_UNITS_PATH)
    df_lat = pd.read_csv(LATENCY_PATH) if os.path.exists(LATENCY_PATH) else None
    
    # 1. Layer Distribution per Area
    fig1, ax1 = plt.subplots(figsize=(14, 6))
    order = ['V1/V2', 'V3/V4', 'MT/MST', 'V4/TEO', 'FEF', 'PFC']
    df_known = df_units[df_units['layer'] != 'unknown']
    
    unique_areas = [o for o in order if o in df_known['area'].unique()]
    layers = ['Superficial', 'L4', 'Deep']
    x = np.arange(len(unique_areas))
    width = 0.25
    
    for i, layer in enumerate(layers):
        counts = [len(df_known[(df_known['area'] == a) & (df_known['layer'] == layer)]) for a in unique_areas]
        ax1.bar(x + (i-1)*width, counts, width, label=layer)
        
    ax1.set_xticks(x)
    ax1.set_xticklabels(unique_areas)
    ax1.set_title("Omission Neuron Distribution by Layer (Corrected Timing)")
    ax1.set_ylabel("Count of Real Omission Units")
    ax1.legend()
    ax1.grid(True, axis='y', alpha=0.3)
    fig1.savefig(os.path.join(OUTPUT_DIR, 'summary_layer_distribution.png'))

    # 2. Omission Index (Ratio) by Area and Layer
    fig2, ax2 = plt.subplots(figsize=(14, 6))
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
    fig2.savefig(os.path.join(OUTPUT_DIR, 'summary_strength_by_layer.png'))

    # 3. Latency Hierarchy Plot
    if df_lat is not None:
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        # Filter to target areas for hierarchy
        df_target = df_lat[df_lat['area'].isin(order)].copy()
        df_target['area'] = pd.Categorical(df_target['area'], categories=order, ordered=True)
        df_target = df_target.sort_values('area')
        
        ax3.barh(df_target['area'].astype(str), df_target['latency_ms'], color='skyblue')
        ax3.set_xlabel("Latency (ms after Omission Onset)")
        ax3.set_title("Omission Signal Hierarchy (Population PSTH Onset)")
        ax3.grid(True, axis='x', alpha=0.3)
        fig3.savefig(os.path.join(OUTPUT_DIR, 'summary_latency_hierarchy.png'))

    print(f"Summary visualizations updated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
