
import numpy as np
import pandas as pd
from pathlib import Path
import re

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def find_complex_omission_neurons():
    df = pd.read_csv(PROFILE_PATH)
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
                rrxr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRXR.npy"
                rrrx_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRX.npy"
                if not rrxr_path.exists() or not rrrx_path.exists(): continue
                
                rrxr_data = np.load(rrxr_path)
                rrrx_data = np.load(rrrx_path)
                
                # Omission Windows
                # p3 (x) in RRXR: indices 3062 to 3593
                # p4 (x) in RRRX: indices 4093 to 4624
                
                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrxr_data.shape[1] or l_idx >= rrrx_data.shape[1]: continue
                    
                    # Mean spikes in omission windows
                    mean_spks_rrxr = rrxr_data[:, l_idx, 3062:3593].sum(axis=1).mean()
                    mean_spks_rrrx = rrrx_data[:, l_idx, 4093:4624].sum(axis=1).mean()
                    
                    # Preceding delay means
                    mean_d2_rrxr = rrxr_data[:, l_idx, 2562:3062].sum(axis=1).mean()
                    mean_d3_rrrx = rrrx_data[:, l_idx, 3593:4093].sum(axis=1).mean()
                    
                    if mean_spks_rrxr > 1.2 * mean_d2_rrxr and mean_spks_rrrx > 1.2 * mean_d3_rrrx:
                        results.append({
                            'session': session, 'probe': probe, 'unit_id_in_session': row['unit_id_in_session'],
                            'local_idx': l_idx, 'area': row['location'],
                            'mean_spks_p3_rrxr': mean_spks_rrxr,
                            'mean_spks_p4_rrrx': mean_spks_rrrx,
                            'ratio_rrxr': mean_spks_rrxr / (mean_d2_rrxr + 1e-6),
                            'ratio_rrrx': mean_spks_rrrx / (mean_d3_rrrx + 1e-6)
                        })
            except: continue
                
    if not results:
        print("No candidates.")
        return
        
    res_df = pd.DataFrame(results)
    print("Candidates for Omission Neuron:")
    # Look for high mean spikes
    print(res_df.sort_values(['mean_spks_p3_rrxr', 'mean_spks_p4_rrrx'], ascending=False).head(10).to_markdown())

if __name__ == "__main__":
    find_complex_omission_neurons()
