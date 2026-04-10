
import numpy as np
import pandas as pd
from pathlib import Path
import re

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def find_complex_omission_neurons():
    df = pd.read_csv(PROFILE_PATH)
    
    # Base Quality: Presence >= 0.99, SNR > 1.0, Location PFC/FEF
    mask = (df['presence_ratio'] >= 0.99) & (df['snr'] > 1.0) & (df['location'].str.contains('PFC|FEF'))
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
                # Load RRXR and RRRX
                rrxr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRXR.npy"
                rrrx_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRX.npy"
                if not rrxr_path.exists() or not rrrx_path.exists(): continue
                
                rrxr_data = np.load(rrxr_path)
                rrrx_data = np.load(rrrx_path)
                
                # RRXR indices (1000 = p1 onset)
                # d2: 1562 to 2062 (indices 2562 to 3062)
                # p3 (x): 2062 to 2593 (indices 3062 to 3593)
                rrxr_d2_fr = rrxr_data[:, :, 2562:3062].mean(axis=(0, 2)) * 1000
                rrxr_p3_fr = rrxr_data[:, :, 3062:3593].mean(axis=(0, 2)) * 1000
                rrxr_p3_spks = rrxr_data[:, :, 3062:3593].sum(axis=2) # (trials, units)
                
                # RRRX indices
                # d3: 2593 to 3093 (indices 3593 to 4093)
                # p4 (x): 3093 to 3624 (indices 4093 to 4624)
                rrrx_d3_fr = rrrx_data[:, :, 3593:4093].mean(axis=(0, 2)) * 1000
                rrrx_p4_fr = rrrx_data[:, :, 4093:4624].mean(axis=(0, 2)) * 1000
                rrrx_p4_spks = rrrx_data[:, :, 4093:4624].sum(axis=2) # (trials, units)
                
                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrxr_data.shape[1] or l_idx >= rrrx_data.shape[1]: continue
                    
                    # 1. More firing during omission than preceding delay
                    if rrxr_p3_fr[l_idx] < rrxr_d2_fr[l_idx]: continue
                    if rrrx_p4_fr[l_idx] < rrrx_d3_fr[l_idx]: continue
                    
                    # 2. Robust spiking during omission presentations (> 10 spikes per trial)
                    # Checking if MIN spikes across trials is > 10
                    min_spks_rrxr = np.min(rrxr_p3_spks[:, l_idx])
                    min_spks_rrrx = np.min(rrrx_p4_spks[:, l_idx])
                    
                    results.append({
                        'session': session, 'probe': probe, 'unit_id_in_session': row['unit_id_in_session'],
                        'local_idx': l_idx, 'area': row['location'],
                        'rrxr_p3_d2_ratio': rrxr_p3_fr[l_idx] / (rrxr_d2_fr[l_idx] + 1e-6),
                        'rrrx_p4_d3_ratio': rrrx_p4_fr[l_idx] / (rrrx_d3_fr[l_idx] + 1e-6),
                        'min_spks_rrxr_p3': min_spks_rrxr,
                        'min_spks_rrrx_p4': min_spks_rrrx
                    })
            except Exception as e:
                # print(f"Error: {e}")
                continue
                
    if not results:
        print("No candidates matching complex omission criteria.")
        return
        
    res_df = pd.DataFrame(results)
    # Sort by joint ratio
    res_df['joint_ratio'] = res_df['rrxr_p3_d2_ratio'] + res_df['rrrx_p4_d3_ratio']
    print("Candidates for Omission Neuron (P3@RRXR, P4@RRRX, min 10 spks):")
    print(res_df.sort_values('joint_ratio', ascending=False).head(10).to_markdown())

if __name__ == "__main__":
    find_complex_omission_neurons()
