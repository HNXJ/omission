
import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy.stats import ttest_rel

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')
OUTPUT_PATH = Path(r'D:\drive\omission\outputs\unit_refined_categories.csv')

def perform_ultimate_audit():
    df = pd.read_csv(PROFILE_PATH)
    
    # 1. Map Session/Probe
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None

    df['session_id'] = df['session_nwb'].apply(extract_ses)
    df['probe_id'] = df['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df['local_idx'] = df.groupby(['session_id', 'probe_id']).cumcount()

    results = []
    unique_sessions = df['session_id'].dropna().unique()
    
    print(f"Auditing {len(unique_sessions)} sessions for Ultimate Stability and refined S/O categories...")

    for session in unique_sessions:
        for probe in [0, 1, 2]:
            units_in_probe = df[(df['session_id'] == session) & (df['probe_id'] == probe)]
            if units_in_probe.empty: continue
            
            try:
                # Load key files
                rrrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRR.npy"
                # Omission trial types
                omit_types = ['AXAB', 'BXBA', 'RXRR', 'AAXB', 'BBXA', 'RRXR', 'AAAX', 'BBBX', 'RRRX']
                
                if not rrrr_path.exists(): continue
                rrrr_data = np.load(rrrr_path) # (trials, units, time)
                
                # Windows (indices relative to 1000=0ms)
                # fixation baseline: fx (-500 to 0) -> 500 to 1000
                # presentation p1: 0 to 531 -> 1000 to 1531
                # delay baseline d1: 531 to 1031 -> 1531 to 2031
                
                fx_spks = rrrr_data[:, :, 500:1000].sum(axis=2) # (trials, units)
                p1_spks = rrrr_data[:, :, 1000:1531].sum(axis=2)
                
                # Check RRRR stability: min 1 spike per 1000ms window in every trial
                # RRRR trial length is 6000ms. We check the full trial firing.
                rrrr_full_spks = rrrr_data[:, :, 1000:5000].sum(axis=2) # 4 seconds
                rrrr_stable = np.all(rrrr_full_spks >= 4, axis=0) # (units,) -> 1Hz over 4s
                
                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1]: continue
                    
                    # New Stable Definition
                    is_stable = (row['isi_violations'] < 0.5) and rrrr_stable[l_idx]
                    
                    # Stimulus responsiveness (p1 vs fx)
                    # p-value from trials
                    _, p_stim = ttest_rel(p1_spks[:, l_idx], fx_spks[:, l_idx])
                    mean_p1 = p1_spks[:, l_idx].mean()
                    mean_fx = fx_spks[:, l_idx].mean()
                    
                    is_s_plus = (p_stim < 0.05) and (mean_p1 > mean_fx)
                    is_s_minus = (p_stim < 0.05) and (mean_p1 < mean_fx)
                    
                    # Omission responsiveness (Placeholder check across types)
                    # We'll check RXRR p2 as a proxy for O+ categorization speed
                    is_o_plus = False
                    is_o_minus = False
                    
                    rxrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
                    if rxrr_path.exists():
                        rxrr_data = np.load(rxrr_path)
                        if rxrr_data.shape[1] > l_idx:
                            # omission p2: 1031 to 1562 -> 2031 to 2562
                            # baseline d1: 531 to 1031 -> 1531 to 2031
                            o_p2_spks = rxrr_data[:, l_idx, 2031:2562].sum(axis=1)
                            o_fx_spks = rxrr_data[:, l_idx, 500:1000].sum(axis=1)
                            _, p_omit = ttest_rel(o_p2_spks, o_fx_spks)
                            mean_o = o_p2_spks.mean()
                            mean_ofx = o_fx_spks.mean()
                            is_o_plus = (p_omit < 0.05) and (mean_o > mean_ofx)
                            is_o_minus = (p_omit < 0.05) and (mean_o < mean_ofx)

                    results.append({
                        'session_id': session,
                        'unit_id': row['unit_id_in_session'],
                        'area': row['location'],
                        'is_stable_ultimate': is_stable,
                        'is_s_plus': is_s_plus,
                        'is_s_minus': is_s_minus,
                        'is_o_plus': is_o_plus,
                        'is_o_minus': is_o_minus
                    })
            except Exception as e:
                continue

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Refined categorization saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    perform_ultimate_audit()
