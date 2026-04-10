
import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy.stats import ttest_rel

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')
OUTPUT_PATH = Path(r'D:\drive\omission\outputs\omission_ratio_groups.csv')

def find_omission_ratio_groups():
    df = pd.read_csv(PROFILE_PATH)
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None
    df['session_id'] = df['session_nwb'].apply(extract_ses)
    df['probe_id'] = df['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df['local_idx'] = df.groupby(['session_id', 'probe_id']).cumcount()

    TOTAL_UNITS = len(df)
    BONFERRONI_ALPHA = 0.05 / TOTAL_UNITS

    results = []
    unique_sessions = df['session_id'].dropna().unique()
    
    OMIT_MAP = {
        'p2': (['AXAB', 'BXBA', 'RXRR'], (2031, 2562)),
        'p3': (['AAXB', 'BBXA', 'RRXR'], (3062, 3593)),
        'p4': (['AAAX', 'BBBX', 'RRRX'], (4093, 4624))
    }

    for session in unique_sessions:
        for probe in [0, 1, 2]:
            units_in_probe = df[(df['session_id'] == session) & (df['probe_id'] == probe)]
            if units_in_probe.empty: continue
            
            try:
                control_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRR.npy"
                if not control_path.exists(): continue
                rrrr_data = np.load(control_path)
                # Check Ultimate Stability (min 1Hz every trial)
                rrrr_stable = np.all(rrrr_data[:, :, 1000:5000].sum(axis=2) >= 4, axis=0)

                # Pre-load omission data
                omit_arrays = {}
                for pos, (conds, window) in OMIT_MAP.items():
                    for cond in conds:
                        p = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-{cond}.npy"
                        if p.exists(): omit_arrays[cond] = (np.load(p), window)

                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1] or not rrrr_stable[l_idx] or row['isi_violations'] >= 0.5:
                        continue

                    o_vals, f_vals, d_vals = [], [], []
                    for cond, (data, window) in omit_arrays.items():
                        if l_idx < data.shape[1]:
                            o_vals.extend(data[:, l_idx, window[0]:window[1]].sum(axis=1))
                            f_vals.extend(data[:, l_idx, 500:1000].sum(axis=1))
                            d_vals.extend(data[:, l_idx, window[0]-500:window[0]].sum(axis=1))

                    if not o_vals: continue
                    _, p_fx = ttest_rel(o_vals, f_vals)
                    _, p_dl = ttest_rel(o_vals, d_vals)
                    m_o, m_f, m_d = np.mean(o_vals), np.mean(f_vals), np.mean(d_vals)
                    
                    ratio = m_o / (m_f + 1e-6)
                    
                    # Basic O+ requirements: Significant increase over baseline and delay
                    if p_fx < BONFERRONI_ALPHA and p_dl < BONFERRONI_ALPHA and m_o > m_f and m_o > m_d:
                        # Bracket it
                        bracket = "none"
                        if ratio >= 2.0: bracket = "2.0+"
                        elif ratio >= 1.75: bracket = "1.75-2.0"
                        elif ratio >= 1.5: bracket = "1.5-1.75"
                        elif ratio >= 1.25: bracket = "1.25-1.5"
                        elif ratio >= 1.01: bracket = "1.01-1.25"
                        
                        if bracket != "none":
                            results.append({
                                'session': session, 'probe': probe, 'unit_id': row['unit_id_in_session'],
                                'local_idx': l_idx, 'area': row['location'], 'ratio': ratio, 'bracket': bracket
                            })
            except: continue

    res_df = pd.DataFrame(results)
    res_df.to_csv(OUTPUT_PATH, index=False)
    print("Omission Ratio Brackets Count:")
    print(res_df['bracket'].value_counts().sort_index())

if __name__ == "__main__":
    find_omission_ratio_groups()
