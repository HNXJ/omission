"""
identify_omission_neurons.py: Detects units with significant firing increases specifically during omissions.
Processes sessions 230831, 230901, and 230720 using granular .npy data.
"""
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

import os
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
import glob

DATA_DIR = str(DATA_DIR)
OUTPUT_DIR = str(PROCESSED_DATA_DIR)
SAMPLING_RATE = 1000 # Spikes are binary 1ms bins

# Area mapping based on probe ID
SESSION_AREAS = {
    '230831': {'0': 'FEF', '1': 'MT', '2': 'V4'},
    '230901': {'0': 'PFC', '1': 'MT', '2': 'V3/V4'},
    '230720': {'0': 'V1/V2', '1': 'V3/V4'}
}

def detect_omission_units(session_id, probe_id):
    area = SESSION_AREAS[session_id].get(probe_id, 'unknown')
    print(f"Processing {session_id} Probe {probe_id} ({area})...")
    
    # We compare standard trials (AAAB) vs Omission trials (AAAX or BBBA if it contains omission)
    # The 'omission' in the task usually happens at the end of the sequence.
    # In our 6000ms window, we'll check the period where the omission occurs.
    # Based on previous scripts, omission window is typically around 4000-5000ms.
    
    baseline_win = (3000, 3500) # Pre-omission period in the sequence
    omission_win = (4000, 5000) # Omission period
    
    # Find all 'X' files (omission conditions)
    omit_files = glob.glob(os.path.join(DATA_DIR, f'ses{session_id}-units-probe{probe_id}-spk-*X*.npy'))
    if not omit_files:
        print(f"  No omission files found for {session_id} P{probe_id}")
        return []

    omission_units = []
    
    for f_path in omit_files:
        cond = os.path.basename(f_path).split('-')[-1].replace('.npy', '')
        print(f"  Analyzing condition: {cond}")
        
        # Load binary spikes (Trials, Units, Samples)
        spikes = np.load(f_path, mmap_mode='r')
        n_trials, n_units, n_samples = spikes.shape
        
        for u in range(n_units):
            # Calculate mean firing rate in windows per trial
            # Summing over 1ms bins gives spike count.
            base_fr = np.sum(spikes[:, u, baseline_win[0]:baseline_win[1]], axis=1)
            omit_fr = np.sum(spikes[:, u, omission_win[0]:omission_win[1]], axis=1)
            
            # Simple threshold + t-test
            mean_base = np.mean(base_fr)
            mean_omit = np.mean(omit_fr)
            
            # Significant increase: Omit > Base and p < 0.05
            if mean_omit > mean_base * 1.5 and mean_omit > 1.0: # Minimum 1 spike average
                t_stat, p_val = ttest_rel(omit_fr, base_fr)
                if p_val < 0.01:
                    omission_units.append({
                        'session_id': session_id,
                        'probe_id': probe_id,
                        'area': area,
                        'unit_idx': u,
                        'condition': cond,
                        'mean_base': mean_base,
                        'mean_omit': mean_omit,
                        'p_val': p_val,
                        'ratio': mean_omit / (mean_base + 1e-6)
                    })
                    
    return omission_units

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_omit_units = []
    
    for sid, probes in SESSION_AREAS.items():
        for pid in probes:
            units = detect_omission_units(sid, pid)
            all_omit_units.extend(units)
            
    df = pd.DataFrame(all_omit_units)
    if not df.empty:
        # Deduplicate (unit might show up in multiple omission conditions)
        df = df.sort_values('ratio', ascending=False).drop_duplicates(subset=['session_id', 'probe_id', 'unit_idx'])
        
        output_path = os.path.join(OUTPUT_DIR, 'omission_units_identified.csv')
        df.to_csv(output_path, index=False)
        print(f"\nFound {len(df)} unique omission neurons across targeted areas.")
        print(df['area'].value_counts())
    else:
        print("\nNo omission neurons detected with current thresholds.")

if __name__ == "__main__":
    main()
