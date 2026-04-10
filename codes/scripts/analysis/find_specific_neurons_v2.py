
import numpy as np
import pandas as pd
from pathlib import Path
import re

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def get_candidates():
    df = pd.read_csv(PROFILE_PATH)
    mask = (df['presence_ratio'] >= 0.99) & (df['firing_rate'] > 5.0) & (df['snr'] > 1.0)
    df_filtered = df[mask].copy()
    
    if df_filtered.empty:
        print("No units match base criteria (PR >= 0.99, Firing > 5, SNR > 1).")
        return

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
                
                rrrr_data = np.load(rrrr_path)
                rxrr_data = np.load(rxrr_path)
                
                # p1, d1, rxrr_p2, rxrr_d1
                p1_fr = rrrr_data[:, :, 1000:1531].mean(axis=(0, 2)) * 1000
                d1_fr = rrrr_data[:, :, 1531:2031].mean(axis=(0, 2)) * 1000
                rxrr_p2_fr = rxrr_data[:, :, 2031:2562].mean(axis=(0, 2)) * 1000
                rxrr_d1_fr = rxrr_data[:, :, 1531:2031].mean(axis=(0, 2)) * 1000
                
                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1]: continue
                    
                    results.append({
                        'session': session, 'probe': probe, 'unit_id_in_session': row['unit_id_in_session'],
                        'local_idx': l_idx, 'area': row['location'],
                        'p1_d1_ratio': p1_fr[l_idx] / (d1_fr[l_idx] + 1e-6),
                        'd1_p1_ratio': d1_fr[l_idx] / (p1_fr[l_idx] + 1e-6),
                        'rxrr_p2_d1_ratio': rxrr_p2_fr[l_idx] / (rxrr_d1_fr[l_idx] + 1e-6)
                    })
            except: continue
                
    if not results:
        print("No units match ratio criteria in the sampled sessions.")
        return
        
    res_df = pd.DataFrame(results)
    print("Candidates found.")
    print(res_df[res_df['p1_d1_ratio'] >= 2.0].sort_values('p1_d1_ratio', ascending=False).head(3).to_markdown())
    print(res_df[res_df['d1_p1_ratio'] >= 2.0].sort_values('d1_p1_ratio', ascending=False).head(3).to_markdown())
    print(res_df[res_df['rxrr_p2_d1_ratio'] >= 2.0].sort_values('rxrr_p2_d1_ratio', ascending=False).head(3).to_markdown())

if __name__ == "__main__":
    get_candidates()
