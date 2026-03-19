"""
identify_real_omission_neurons_v2.py: Exploratory detection of Omission units.
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
import glob

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'

# Sequence Logic: 
FIXATION_WIN = (0, 500)
SEQUENCE_WIN = (1000, 3900)
OMISSION_WIN = (4000, 5000)

SESSION_AREAS = {
    '230831': {'0': 'FEF', '1': 'MT', '2': 'V4'},
    '230901': {'0': 'PFC', '1': 'MT', '2': 'V3/V4'},
    '230720': {'0': 'V1/V2', '1': 'V3/V4'},
    '230818': {'0': 'PFC', '1': 'MT', '2': 'V4'} # Adding 230818 for reference
}

def detect(session_id, probe_id):
    area = SESSION_AREAS[session_id].get(probe_id, 'unknown')
    omit_files = glob.glob(os.path.join(DATA_DIR, f'ses{session_id}-units-probe{probe_id}-spk-*X*.npy'))
    if not omit_files: return []
    
    results = []
    for f_path in omit_files:
        cond = os.path.basename(f_path).split('-')[-1].replace('.npy', '')
        spikes = np.load(f_path, mmap_mode='r')
        n_trials, n_units, _ = spikes.shape
        
        for u in range(n_units):
            fix = np.mean(np.sum(spikes[:, u, 0:500], axis=1))
            seq = np.mean(np.sum(spikes[:, u, 1000:3900], axis=1)) / 2900 * 500
            omit = np.mean(np.sum(spikes[:, u, 4000:4800], axis=1)) / 800 * 500
            
            # Record everything that has some increase in omission
            if omit > fix * 1.5 and omit > seq * 1.5 and omit > 0.5:
                results.append({
                    'sid': session_id, 'pid': probe_id, 'area': area, 'u': u, 'cond': cond,
                    'fix': fix, 'seq': seq, 'omit': omit,
                    'r_fix': omit/max(fix, 1e-6), 'r_seq': omit/max(seq, 1e-6)
                })
    return results

def main():
    all_res = []
    for sid, probes in SESSION_AREAS.items():
        for pid in probes:
            all_res.extend(detect(sid, pid))
    
    df = pd.DataFrame(all_res)
    if not df.empty:
        df = df.sort_values('r_fix', ascending=False)
        df.to_csv(os.path.join(OUTPUT_DIR, 'omission_exploratory.csv'), index=False)
        print(f"Found {len(df)} potential units.")
        print(df.head(20))
    else:
        print("Nothing found.")

if __name__ == "__main__":
    main()
