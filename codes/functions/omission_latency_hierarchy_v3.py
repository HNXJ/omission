"""
omission_latency_hierarchy_v3.py: Compares onset latencies of omission signals across areas.
Uses 'Real' units and aligns to the p4 omission slot (4093ms). Calculates latency per area.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

UNITS_LAYERED_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/real_omission_units_layered_v3.csv'
LATENCY_OUTPUT_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/omission_latencies_v3.csv' # Save to new file
DATA_DIR = 'D:/Analysis/Omission/local-workspace/data'

def calculate_latency(sid, pid, uid, cond):
    fpath = os.path.join(DATA_DIR, f'ses{sid}-units-probe{pid}-spk-{cond}.npy')
    if not os.path.exists(fpath): return np.nan
    
    spikes = np.load(fpath, mmap_mode='r')
    # Alignment: p1 at 1000. p4 onset at 4093.
    # Window for latency check: 4093 to 5000.
    omit_onset = 4093
    
    # PSTH
    psth = np.mean(spikes[:, uid, :], axis=0) * 1000 # Hz
    
    # Baseline: Fixation (500 to 1000)
    baseline_avg = np.mean(psth[500:1000])
    baseline_std = np.std(psth[500:1000])
    
    thresh = baseline_avg + 2.0 * baseline_std # Relaxed threshold
    
    # Look for first crossing after omit_onset (within the next 500ms, as omit_win is 4093-4624)
    search_win = psth[omit_onset:omit_onset+500] 
    over = np.where(search_win > thresh)[0]
    
    for o in over:
        # Persistence check: 10ms
        if o + 10 < len(search_win) and np.all(search_win[o:o+10] > thresh):
            return o # ms after omission onset (relative to omit_onset)
            
    return np.nan

def main():
    if not os.path.exists(UNITS_LAYERED_PATH):
        print(f"Error: Units layered file not found at {UNITS_LAYERED_PATH}")
        return
    
    df_units = pd.read_csv(UNITS_LAYERED_PATH)
    df_units['session_id'] = df_units['session_id'].astype(str)
    df_units['probe_id'] = df_units['probe_id'].astype(str)
    df_units['unit_idx'] = df_units['unit_idx'].astype(int)

    print(f"Calculating latencies for {len(df_units)} units...")
    latencies = []
    
    # Group by session, probe, and area to process each unique unit group
    for (sid, pid, area), group in df_units.groupby(['session_id', 'probe_id', 'area']):
        # Select top units by r_fix for representative latency
        top_units_in_group = group.sort_values('r_fix', ascending=False).head(10) # Get top 10 units per group
        
        for _, row in top_units_in_group.iterrows():
            lat = calculate_latency(row['session_id'], row['probe_id'], row['unit_idx'], row['cond'])
            latencies.append({
                'session_id': row['session_id'],
                'area': row['area'],
                'probe_id': row['probe_id'],
                'unit_idx': row['unit_idx'],
                'layer': row['layer'],
                'latency_ms': lat
            })
            
    df_lat = pd.DataFrame(latencies)
    df_lat.to_csv(LATENCY_OUTPUT_PATH, index=False)
    
    # Hierarchy Summary
    summary = df_lat.groupby('area').agg(
        unit_count=('latency_ms', 'count'),
        median_latency_ms=('latency_ms', lambda x: np.nanmedian(x) if not x.isnull().all() else np.nan)
    ).reset_index()
    
    # Clean up infinite values
    summary['median_latency_ms'] = summary['median_latency_ms'].replace([np.inf, -np.inf], np.nan)
    
    print("
Latency Hierarchy (Median ms after Omission Onset):")
    print(summary.sort_values('median_latency_ms'))

if __name__ == "__main__":
    main()
