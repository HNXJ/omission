"""
omission_latency_hierarchy.py: Compares onset latencies of omission signals across brain areas.
Analyzes both Spikes (from identified units) and LFP (from high-PEV channels).
"""
import os
import numpy as np
import pandas as pd
import glob

OMIT_UNITS_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_layered.csv'
LFP_PEV_PATH = r'D:\Analysis\Omission\local-workspace\LFP_Extractions\omission_lfp_pev.npz'
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'

def calculate_spike_latency(session_id, probe_id, unit_idx):
    # Find one omission file
    files = glob.glob(os.path.join(DATA_DIR, f'ses{session_id}-units-probe{probe_id}-spk-*X*.npy'))
    if not files: return np.nan
    
    # We'll use the first one (usually AAAX)
    spikes = np.load(files[0], mmap_mode='r')
    # Omission onset is at t=4000ms
    # Check window 4000-5000ms
    omit_spikes = spikes[:, unit_idx, 4000:5000] # (Trials, Time)
    
    # Simple latency: first timepoint where PSTH exceeds baseline + 3SD
    psth = np.mean(omit_spikes, axis=0)
    # Use 0-500ms as true baseline
    baseline = np.mean(spikes[:, unit_idx, 0:500], axis=(0,1))
    std = np.std(np.mean(spikes[:, unit_idx, 0:500], axis=0))
    
    thresh = baseline + 3 * std
    over = np.where(psth > thresh)[0]
    if len(over) > 0:
        # Require 10ms of persistence to avoid noise
        for o in over:
            if o + 10 < len(psth) and np.all(psth[o:o+10] > thresh):
                return o
    return np.nan

def calculate_lfp_latency(pev_data):
    # pev_data: (Channels, Time) for 4000-5000ms
    # Latency: timepoint where PEV exceeds 5% of variance
    avg_pev = np.mean(pev_data, axis=0)
    thresh = 0.05
    over = np.where(avg_pev > thresh)[0]
    if len(over) > 0:
        return over[0]
    return np.nan

def main():
    if not os.path.exists(OMIT_UNITS_PATH): return
    df_omit = pd.read_csv(OMIT_UNITS_PATH)
    # Filter for "Real"
    df_omit = df_omit[(df_omit['r_fix'] > 2.0) & (df_omit['r_seq'] > 2.0)]
    
    lfp_pev = np.load(LFP_PEV_PATH)
    
    # 1. Compute latencies for units
    print(f"Computing latencies for {len(df_omit)} 'Real' omission units...")
    latencies = []
    for (sid, area), group in df_omit.groupby(['session_id', 'area']):
        top_units = group.sort_values('r_fix', ascending=False).head(20)
        for _, row in top_units.iterrows():
            lat = calculate_spike_latency(str(int(row['session_id'])), str(int(row['probe_id'])), int(row['unit_idx']))
            latencies.append({
                'session_id': row['session_id'],
                'area': row['area'],
                'layer': row['layer'],
                'latency_ms': lat
            })
            
    df_lat = pd.DataFrame(latencies)
    
    # 2. Compute latencies for LFP
    print("Computing latencies for LFP PEV...")
    lfp_latencies = []
    for key in lfp_pev.files:
        sid, area = key.split('_', 1)
        lat = calculate_lfp_latency(lfp_pev[key])
        lfp_latencies.append({
            'session_id': sid,
            'area': area,
            'lfp_latency_ms': lat
        })
    df_lfp_lat = pd.DataFrame(lfp_latencies)
    
    # Summary
    print("\nSummary of Latencies (Median):")
    if not df_lat.empty:
        summary = df_lat.groupby(['area']).agg({'latency_ms': 'median'}).sort_values('latency_ms')
        print(summary)
    
    df_lat.to_csv(os.path.join(OUTPUT_DIR, 'omission_latencies_spikes_real.csv'), index=False)
    df_lfp_lat.to_csv(os.path.join(OUTPUT_DIR, 'omission_latencies_lfp.csv'), index=False)

if __name__ == "__main__":
    main()
