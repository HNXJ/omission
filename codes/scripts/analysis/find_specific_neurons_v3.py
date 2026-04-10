
import numpy as np
import pandas as pd
from pathlib import Path
import re

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def get_candidates():
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
                rrrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRR.npy"
                rxrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
                if not rrrr_path.exists() or not rxrr_path.exists(): continue
                
                rrrr_data = np.load(rrrr_path) # (trials, units, time)
                rxrr_data = np.load(rxrr_path)
                
                # Full Trial Mean (RRRR)
                rrrr_full_fr = rrrr_data.mean(axis=(0, 2)) * 1000
                
                # p1, d1 (RRRR)
                p1_fr = rrrr_data[:, :, 1000:1531].mean(axis=(0, 2)) * 1000
                d1_fr = rrrr_data[:, :, 1531:2031].mean(axis=(0, 2)) * 1000
                
                # rxrr_p2, rxrr_d1 (RXRR)
                rxrr_p2_fr = rxrr_data[:, :, 2031:2562].mean(axis=(0, 2)) * 1000
                rxrr_d1_fr = rxrr_data[:, :, 1531:2031].mean(axis=(0, 2)) * 1000
                
                for i, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1]: continue
                    
                    # New Base Criterion: Average RRRR firing > 1.0 Hz
                    if rrrr_full_fr[l_idx] <= 1.0: continue
                    
                    val_p1, val_d1 = p1_fr[l_idx], d1_fr[l_idx]
                    val_rxrr_p2, val_rxrr_d1 = rxrr_p2_fr[l_idx], rxrr_d1_fr[l_idx]
                    
                    results.append({
                        'session': session, 'probe': probe, 'unit_id_in_session': row['unit_id_in_session'],
                        'local_idx': l_idx, 'area': row['location'],
                        'rrrr_fr': rrrr_full_fr[l_idx],
                        's_plus_ratio': val_p1 / (val_d1 + 1e-6),
                        's_minus_ratio': val_d1 / (val_p1 + 1e-6),
                        'o_plus_ratio': val_rxrr_p2 / (val_rxrr_d1 + 1e-6)
                    })
            except: continue
                
    if not results:
        print("No units match criteria.")
        return
        
    res_df = pd.DataFrame(results)
    
    print("Candidates for S+ (p1 > 2*d1):")
    print(res_df[res_df['s_plus_ratio'] >= 2.0].sort_values('s_plus_ratio', ascending=False).head(3).to_markdown())
    
    print("\nCandidates for S- (d1 > 2*p1):")
    print(res_df[res_df['s_minus_ratio'] >= 2.0].sort_values('s_minus_ratio', ascending=False).head(3).to_markdown())
    
    print("\nCandidates for O+ (RXRR p2 > 2*d1):")
    print(res_df[res_df['o_plus_ratio'] >= 2.0].sort_values('o_plus_ratio', ascending=False).head(3).to_markdown())

if __name__ == "__main__":
    get_candidates()
