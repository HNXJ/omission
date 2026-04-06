"""
identify_real_omission_neurons.py: Detects "Real" omission neurons using corrected 1000ms offset.
Criteria: High firing ONLY during omission, not during fixation or stimulus sequence.
"""
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

import os
import numpy as np
import pandas as pd
import glob

DATA_DIR = str(DATA_DIR)
OUTPUT_DIR = str(PROCESSED_DATA_DIR)

# Timing Windows (relative to file start, p1 onset = 1000)
FIX_WIN = (500, 1000)
P1_WIN = (1000, 1531)
D1_WIN = (1531, 2031)
P2_WIN = (2031, 2562)
D2_WIN = (2562, 3062)
P3_WIN = (3062, 3593)
D3_WIN = (3593, 4093)
P4_WIN = (4093, 4624)

SESSION_AREAS = {
    '230629': {'0': 'V1/V2', '1': 'V3/V4'},
    '230630': {'0': 'PFC', '1': 'V1/V3', '2': 'V4/MT'},
    '230714': {'0': 'V1/V2', '1': 'V3/V4'},
    '230719': {'0': 'DP', '1': 'V1/V2', '2': 'V3/V4'},
    '230720': {'0': 'V1/V2', '1': 'V3/V4'},
    '230721': {'0': 'V1/V2', '1': 'V3/V4'},
    '230816': {'0': 'PFC', '1': 'V1/V3', '2': 'V4/MT'},
    '230818': {'0': 'MT/MST', '1': 'PFC', '2': 'TEO/FST'},
    '230823': {'0': 'FEF', '1': 'MT/MST', '2': 'V1/V2/V3'},
    '230825': {'0': 'MT/MST', '1': 'PFC', '2': 'V4/TEO'},
    '230830': {'0': 'PFC', '1': 'V1/V3', '2': 'V4/MT'},
    '230831': {'0': 'FEF', '1': 'MT/MST', '2': 'V4/TEO'},
    '230901': {'0': 'MT/MST', '1': 'PFC', '2': 'V3/V4'}
}

def detect(session_id, probe_id):
    area = SESSION_AREAS.get(session_id, {}).get(probe_id, 'unknown')
    # Use AAAX, AXAB, AAXB for omission detection
    omit_patterns = ['*AAAX*', '*AXAB*', '*AAXB*', '*BBBX*', '*BXBA*', '*BBXA*', '*RRRX*', '*RXRR*', '*RRXR*']
    
    omit_files = []
    for p in omit_patterns:
        omit_files.extend(glob.glob(os.path.join(DATA_DIR, f'ses{session_id}-units-probe{probe_id}-spk-{p}.npy')))
    
    if not omit_files: return []
    
    results = []
    for f_path in omit_files:
        cond = os.path.basename(f_path).split('-')[-1].replace('.npy', '')
        spikes = np.load(f_path, mmap_mode='r')
        n_trials, n_units, _ = spikes.shape
        
        # Determine omission window for this condition
        if 'AXAB' in cond or 'BXBA' in cond or 'RXRR' in cond:
            omit_win = P2_WIN
            seq_win = (1000, 2031) # p1-d1
        else: # AAAX, AAXB etc
            # This logic needs to be refined for AAAX, AAXB and RRRX, RRXR
            # For now, let's assume it covers P3 and P4 based on the original intent
            if 'AAXB' in cond or 'BBXA' in cond or 'RRXR' in cond:
                omit_win = P3_WIN
                seq_win = (1000, 3062) # p1-d2
            else: # AAAX, BBBX, RRRX
                omit_win = P4_WIN
                seq_win = (1000, 4093) # p1-d3
            
        for u in range(n_units):
            # Calculate rates (Hz)
            def get_rate(win):
                # Ensure the window is within bounds
                start = max(0, win[0])
                end = min(spikes.shape[2], win[1])
                if end <= start: return 0.0 # Handle invalid window
                return np.mean(np.sum(spikes[:, u, start:end], axis=1)) / (end-start) * 1000
            
            fix_rate = get_rate(FIX_WIN)
            seq_rate = get_rate(seq_win)
            omit_rate = get_rate(omit_win)
            
            # "Real" Criteria: 
            # 1. Omit > Fix * 2
            # 2. Omit > Seq * 2
            # 3. Seq should be within 0.5x to 1.5x of Fix (no stim drive, no inhibition)
            if omit_rate > 1.0 and omit_rate > fix_rate * 2.0 and omit_rate > seq_rate * 2.0:
                if seq_rate > fix_rate * 0.5 and seq_rate < fix_rate * 1.5:
                    results.append({
                        'sid': session_id, 'pid': probe_id, 'area': area, 'u': u, 'cond': cond,
                        'fix': fix_rate, 'seq': seq_rate, 'omit': omit_rate,
                        'r_fix': omit_rate/max(fix_rate, 0.1), 'r_seq': omit_rate/max(seq_rate, 0.1)
                    })
    return results

def main():
    all_res = []
    for sid in SESSION_AREAS:
        for pid in SESSION_AREAS[sid]:
            all_res.extend(detect(sid, pid))
    
    df = pd.DataFrame(all_res)
    if not df.empty:
        # Deduplicate: if a unit is 'Real' in multiple conditions, keep the best ratio
        df = df.sort_values('r_fix', ascending=False).drop_duplicates(subset=['sid', 'pid', 'u'])
        df.to_csv(os.path.join(OUTPUT_DIR, 'real_omission_units.csv'), index=False)
        print(f"Found {len(df)} 'Real' omission units.")
        print(df['area'].value_counts())
    else:
        print("No units found.")

if __name__ == "__main__":
    main()
