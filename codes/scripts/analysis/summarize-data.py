"""
summarize_neuron_data.py: Aggregates omission neuron data by area, layer, and response strength.
Handles potential NaNs in latency.
"""
import os
import pandas as pd
import numpy as np

# Paths
UNITS_LAYERED_PATH = r'D:\Analysis\Omission\local-workspace\checkpointseal_omission_units_layered_v3.csv'
LATENCY_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\omission_latencies_v2.csv' # Updated to use the latest latency file
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\summary_stats'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    df_units = pd.read_csv(UNITS_PATH)
    df_lat = pd.read_csv(LATENCY_PATH)
    
    # Merge unit data with latency data
    # Ensure column names are consistent, and handle potential missing latency data
    df_units = df_units.rename(columns={'session_id': 'session_id', 'probe_id': 'probe_id', 'unit_idx': 'unit_idx'})
    df_lat = df_lat.rename(columns={'session_id': 'session_id', 'probe_id': 'probe_id', 'unit_idx': 'unit_idx'})
    
    # Merge, keeping all units and adding latency where available
    merged_df = pd.merge(df_units, df_lat, on=['session_id', 'probe_id', 'unit_idx', 'area', 'layer'], how='left')
    
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
    strength_bins = [-np.inf, 1.5, 2.0, 5.0, np.inf] # Adjusted bins based on findings
    strength_labels = ['Low (<1.5x)', 'Baseline-like (1.5-2x)', 'Medium (2-5x)', 'High (>5x)']
    merged_df['strength_bin'] = pd.cut(merged_df['r_fix'], bins=strength_bins, labels=strength_labels, right=False)
    
    strength_area_summary = merged_df.groupby(['strength_bin', 'area']).agg(
        neuron_count=('unit_idx', 'size')
    ).reset_index()
    strength_layer_summary = merged_df.groupby(['strength_bin', 'layer']).agg(
        neuron_count=('unit_idx', 'size')
    ).reset_index()
    
    strength_area_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_neurons_by_strength_area.csv'), index=False)
    strength_layer_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_neurons_by_strength_layer.csv'), index=False)
    print("Saved neuron summaries by signal strength.")
    
    # 4. LFP PEV Summary (Basic aggregation per area)
    try:
        pev_data = np.load(PEV_PATH, allow_pickle=True)
        lfp_summary_data = []
        for key in pev_data.files:
            session_id, area_probe = key.split('_', 1)
            area = area_probe.split('-')[0] # e.g., V1, PFC
            
            pev_vals = pev_data[key] # Shape (Channels, Time)
            avg_pev = np.mean(pev_vals)
            median_pev = np.median(pev_vals)
            
            lfp_summary_data.append({'session_id': session_id, 'area': area, 'avg_PEV': avg_pev, 'median_PEV': median_pev})
            
        df_lfp_summary = pd.DataFrame(lfp_summary_data)
        df_lfp_summary.to_csv(os.path.join(OUTPUT_DIR, 'summary_lfp_pev_by_area.csv'), index=False)
        print("Saved LFP PEV summary.")
    except FileNotFoundError:
        print("LFP PEV file not found. Skipping LFP summary.")
    except Exception as e:
        print(f"Error processing LFP PEV data: {e}")

if __name__ == "__main__":
    main()
