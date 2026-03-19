"""
summarize_neuron_data_v2.py: Aggregates neuron data (counts, r_fix, latency) by area, layer, and signal strength.
Handles NaNs and uses latest CSVs.
"""
import os
import pandas as pd
import numpy as np

# Paths
UNITS_LAYERED_PATH = r'D:\Analysis\Omission\local-workspace\checkpointseal_omission_units_layered_v3.csv'
LATENCY_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\omission_latencies_v2.csv'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\summary_stats'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    df_units = pd.read_csv(UNITS_LAYERED_PATH)
    df_lat = pd.read_csv(LATENCY_PATH)
    
    # Standardize column names for merging
    df_units = df_units.rename(columns={'session_id': 'session_id', 'probe_id': 'probe_id', 'unit_idx': 'unit_idx'})
    df_lat = df_lat.rename(columns={'session_id': 'session_id', 'probe_id': 'probe_id', 'unit_idx': 'unit_idx'})
    
    # Merge unit data with latency data
    # Use 'left' merge to keep all units and add latency where available
    merged_df = pd.merge(df_units, df_lat, on=['session_id', 'area', 'layer', 'unit_idx', 'probe_id'], how='left')
    
    # --- Aggregations ---
    
    # 1. Summary by Area
    area_summary = merged_df.groupby('area').agg(
        neuron_count=('unit_idx', 'size'),
        mean_r_fix=('r_fix', lambda x: np.nanmean(x) if not x.isnull().all() else np.nan),
        median_latency_ms=('latency_ms', lambda x: np.nanmedian(x) if not x.isnull().all() else np.nan)
    ).reset_index()
    area_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_neurons_by_area.csv'), index=False)
    print("Saved neuron summary by area.")

    # 2. Summary by Layer
    layer_summary = merged_df.groupby('layer').agg(
        neuron_count=('unit_idx', 'size'),
        mean_r_fix=('r_fix', lambda x: np.nanmean(x) if not x.isnull().all() else np.nan),
        median_latency_ms=('latency_ms', lambda x: np.nanmedian(x) if not x.isnull().all() else np.nan)
    ).reset_index()
    layer_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_neurons_by_layer.csv'), index=False)
    print("Saved neuron summary by layer.")

    # 3. Summary by Signal Strength (r_fix bins)
    strength_bins = [-np.inf, 1.5, 2.0, 5.0, np.inf] # Adjusted bins
    strength_labels = ['Low (<1.5x)', 'Baseline-like (1.5-2x)', 'Medium (2-5x)', 'High (>5x)']
    merged_df['strength_bin'] = pd.cut(merged_df['r_fix'], bins=strength_bins, labels=strength_labels, right=False)
    
    # Handle cases where strength_bin might result in NaNs if r_fix is NaN
    merged_df['strength_bin'] = merged_df['strength_bin'].astype(str).replace('nan', 'Unknown')

    strength_area_summary = merged_df.groupby(['strength_bin', 'area']).agg(
        neuron_count=('unit_idx', 'size')
    ).reset_index()
    strength_layer_summary = merged_df.groupby(['strength_bin', 'layer']).agg(
        neuron_count=('unit_idx', 'size')
    ).reset_index()
    
    strength_area_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_neurons_by_strength_area.csv'), index=False)
    strength_layer_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_neurons_by_strength_layer.csv'), index=False)
    print("Saved neuron summaries by signal strength.")

if __name__ == "__main__":
    main()
