
import numpy as np
import pandas as pd
from pathlib import Path
import re

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def get_candidates():
    df = pd.read_csv(PROFILE_PATH)
    
    # Basic Filter
    mask = (df['presence_ratio'] > 0.98) & (df['firing_rate'] > 5.0) & (df['snr'] > 1.0)
    df_filtered = df[mask].copy()
    
    # Helper to map session/probe
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None

    df_filtered['session_id'] = df_filtered['session_nwb'].apply(extract_ses)
    df_filtered['probe_id'] = df_filtered['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df_filtered['local_idx'] = df_filtered.groupby(['session_id', 'probe_id']).cumcount()

    results = []
    
    # Sample a few sessions to find candidates quickly
    unique_sessions = df_filtered['session_id'].dropna().unique()
    
    for session in unique_sessions:
        for probe in [0, 1, 2]:
            units_in_probe = df_filtered[(df_filtered['session_id'] == session) & (df_filtered['probe_id'] == probe)]
            if units_in_probe.empty: continue
            
            # Load RRRR and RXRR
            try:
                rrrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRR.npy"
                rxrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
                
                if not rrrr_path.exists() or not rxrr_path.exists(): continue
                
                rrrr_data = np.load(rrrr_path) # (trials, units, time)
                rxrr_data = np.load(rxrr_path)
                
                # Epoch indices (1000 = 0ms)
                # p1: 1000 to 1531
                # d1: 1531 to 2031
                # p2: 2031 to 2562
                
                # Calculate mean FR in epochs
                # RRRR
                p1_fr = rrrr_data[:, :, 1000:1531].mean(axis=(0, 2)) * 1000
                d1_fr = rrrr_data[:, :, 1531:2031].mean(axis=(0, 2)) * 1000
                
                # RXRR
                rxrr_d1_fr = rxrr_data[:, :, 1531:2031].mean(axis=(0, 2)) * 1000
                rxrr_p2_fr = rxrr_data[:, :, 2031:2562].mean(axis=(0, 2)) * 1000
                
                for i, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1]: continue
                    
                    val_p1 = p1_fr[l_idx]
                    val_d1 = d1_fr[l_idx]
                    val_rxrr_p2 = rxrr_p2_fr[l_idx]
                    val_rxrr_d1 = rxrr_d1_fr[l_idx]
                    
                    results.append({
                        'session': session,
                        'probe': probe,
                        'unit_id_in_session': row['unit_id_in_session'],
                        'local_idx': l_idx,
                        'area': row['location'],
                        'p1_d1_ratio': val_p1 / (val_d1 + 1e-6),
                        'd1_p1_ratio': val_d1 / (val_p1 + 1e-6),
                        'rxrr_p2_d1_ratio': val_rxrr_p2 / (val_rxrr_d1 + 1e-6)
                    })
                    
            except Exception as e:
                # print(f"Error processing {session} {probe}: {e}")
                continue
                
    res_df = pd.DataFrame(results)
    
    # Neuron 1: p1 > 2*d1
    n1 = res_df[res_df['p1_d1_ratio'] >= 2.0].sort_values('p1_d1_ratio', ascending=False).head(5)
    
    # Neuron 2: d1 > 2*p1
    n2 = res_df[res_df['d1_p1_ratio'] >= 2.0].sort_values('d1_p1_ratio', ascending=False).head(5)
    
    # Neuron 3: p2(RXRR) > 2*d1(RXRR)
    n3 = res_df[res_df['rxrr_p2_d1_ratio'] >= 2.0].sort_values('rxrr_p2_d1_ratio', ascending=False).head(5)
    
    print("Candidates for Neuron 1 (p1 > 2*d1):")
    print(n1.to_markdown())
    print("\nCandidates for Neuron 2 (d1 > 2*p1):")
    print(n2.to_markdown())
    print("\nCandidates for Neuron 3 (p2(RXRR) > 2*d1(RXRR)):")
    print(n3.to_markdown())

if __name__ == "__main__":
    get_candidates()
