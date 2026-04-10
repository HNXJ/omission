
import numpy as np
import pandas as pd
from pathlib import Path
import re

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def get_ultimate_candidates():
    df = pd.read_csv(PROFILE_PATH)
    
    # Base Quality: Presence >= 0.99, SNR > 1.0
    mask = (df['presence_ratio'] >= 0.99) & (df['snr'] > 1.0)
    df_filtered = df[mask].copy()
    
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None

    df_filtered['session_id'] = df_filtered['session_nwb'].apply(extract_ses)
    df_filtered['probe_id'] = df_filtered['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df_filtered['local_idx'] = df_filtered.groupby(['session_id', 'probe_id']).cumcount()

    results = []
    unique_sessions = df_filtered['session_id'].dropna().unique()
    
    for session in unique_sessions:
        for probe in [0, 1, 2]:
            units_in_probe = df_filtered[(df_filtered['session_id'] == session) & (df_filtered['probe_id'] == probe)]
            if units_in_probe.empty: continue
            
            try:
                # Load key conditions for stability check
                rrrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRR.npy"
                rxrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
                if not rrrr_path.exists() or not rxrr_path.exists(): continue
                
                rrrr_data = np.load(rrrr_path) # (trials, units, time)
                rxrr_data = np.load(rxrr_path)
                
                # Time window for stability check: 0 to 4000ms (indices 1000 to 5000)
                # Length = 4.0 seconds
                stability_window = (1000, 5000)
                
                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1]: continue
                    
                    # Trial-by-trial spike counts in RRRR
                    rrrr_spks_per_trial = rrrr_data[:, l_idx, stability_window[0]:stability_window[1]].sum(axis=1)
                    
                    # Ultimate Stability Criterion:
                    # 1. Min 5 spikes per trial (in 4s window)
                    # 2. This implies >= 1.25 Hz per trial
                    if np.any(rrrr_spks_per_trial < 5): continue
                    
                    # Calculate ratios for categorization
                    # p1, d1 (RRRR)
                    p1_fr = rrrr_data[:, l_idx, 1000:1531].mean() * 1000
                    d1_fr = rrrr_data[:, l_idx, 1531:2031].mean() * 1000
                    
                    # rxrr_p2, rxrr_d1 (RXRR)
                    rxrr_p2_fr = rxrr_data[:, l_idx, 2031:2562].mean() * 1000
                    rxrr_d1_fr = rxrr_data[:, l_idx, 1531:2031].mean() * 1000
                    
                    results.append({
                        'session': session, 'probe': probe, 'unit_id_in_session': row['unit_id_in_session'],
                        'local_idx': l_idx, 'area': row['location'],
                        'min_spks_trial': np.min(rrrr_spks_per_trial),
                        'avg_fr': np.mean(rrrr_spks_per_trial) / 4.0,
                        's_plus_ratio': p1_fr / (d1_fr + 1e-6),
                        's_minus_ratio': d1_fr / (p1_fr + 1e-6),
                        'o_plus_ratio': rxrr_p2_fr / (rxrr_d1_fr + 1e-6)
                    })
            except: continue
                
    if not results:
        print("No ultimate stable units found.")
        return
        
    res_df = pd.DataFrame(results)
    
    print("Ultimate Candidates found.")
    print("\nTop S+:")
    print(res_df[res_df['s_plus_ratio'] >= 2.0].sort_values('s_plus_ratio', ascending=False).head(3).to_markdown())
    print("\nTop S-:")
    print(res_df[res_df['s_minus_ratio'] >= 2.0].sort_values('s_minus_ratio', ascending=False).head(3).to_markdown())
    print("\nTop O+:")
    print(res_df[res_df['o_plus_ratio'] >= 2.0].sort_values('o_plus_ratio', ascending=False).head(3).to_markdown())

if __name__ == "__main__":
    get_ultimate_candidates()
