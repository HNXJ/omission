"""
omission_latency_hierarchy_v2.py: Compares onset latencies of omission signals across areas.
Uses 'Real' units and aligns to the p4 omission slot (4093ms).
"""
import os
import numpy as np
import pandas as pd
import glob

LAYERED_UNITS_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_layered_v3.csv'
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'

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
    
    thresh = baseline_avg + 2 * baseline_std
    
    # Look for first crossing after omit_onset
    search_win = psth[omit_onset:omit_onset+500]
    over = np.where(search_win > thresh)[0]
    
    for o in over:
        # Persistence check: 10ms
        if o + 10 < len(search_win) and np.all(search_win[o:o+10] > thresh):
            return o # ms after omission onset
            
    return np.nan

def main():
    df = pd.read_csv(LAYERED_UNITS_PATH)
    # Filter for robust units
    df = df[(df['layer'] != 'unknown')]
    
    print(f"Calculating latencies for {len(df)} units...")
    latencies = []
    
    for _, row in df.iterrows():
        lat = calculate_latency(row['session_id'], row['probe_id'], row['unit_idx'], row['cond'])
        latencies.append({
            'session_id': row['session_id'],
            'area': row['area'],
            'layer': row['layer'],
            'latency_ms': lat
        })
        
    df_lat = pd.DataFrame(latencies)
    df_lat.to_csv(os.path.join(OUTPUT_DIR, 'omission_latencies_v2.csv'), index=False)
    
    # Hierarchy Summary
    summary = df_lat.groupby('area').agg({'latency_ms': ['median', 'count']})
    print("\nLatency Hierarchy (Median ms after Omission Onset):")
    print(summary.sort_values(('latency_ms', 'median')))

if __name__ == "__main__":
    main()
