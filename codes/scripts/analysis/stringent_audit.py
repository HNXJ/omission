
import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy.stats import ttest_rel

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')
OUTPUT_PATH = Path(r'D:\drive\omission\outputs\unit_refined_categories_v2.csv')

def perform_stringent_audit():
    df = pd.read_csv(PROFILE_PATH)
    
    # Map Identifiers
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None
    df['session_id'] = df['session_nwb'].apply(extract_ses)
    df['probe_id'] = df['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df['local_idx'] = df.groupby(['session_id', 'probe_id']).cumcount()

    # family-wise alpha
    TOTAL_UNITS = len(df)
    BONFERRONI_ALPHA = 0.05 / TOTAL_UNITS
    print(f"Total Units: {TOTAL_UNITS} | Bonferroni Threshold: {BONFERRONI_ALPHA:.2e}")

    results = []
    unique_sessions = df['session_id'].dropna().unique()
    
    # Omission Mappings
    # p2: AXAB, BXBA, RXRR (indices 2031:2562)
    # p3: AAXB, BBXA, RRXR (indices 3062:3593)
    # p4: AAAX, BBBX, RRRX (indices 4093:4624)
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
                # 1. Check Ultimate Stability in RRRR
                rrrr_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RRRR.npy"
                if not rrrr_path.exists(): continue
                rrrr_data = np.load(rrrr_path)
                # 4s trial window (1000 to 5000)
                rrrr_full_spks = rrrr_data[:, :, 1000:5000].sum(axis=2)
                rrrr_stable = np.all(rrrr_full_spks >= 4, axis=0) # 1Hz min per trial

                # 2. Gather Omission vs Baseline data
                omit_spks_all = {l: [] for l in units_in_probe['local_idx']}
                fx_spks_all = {l: [] for l in units_in_probe['local_idx']}
                
                for pos, (conds, window) in OMIT_MAP.items():
                    for cond in conds:
                        path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-{cond}.npy"
                        if not path.exists(): continue
                        data = np.load(path) # (trials, units, time)
                        for _, row in units_in_probe.iterrows():
                            l_idx = row['local_idx']
                            if l_idx < data.shape[1]:
                                omit_spks_all[l_idx].extend(data[:, l_idx, window[0]:window[1]].sum(axis=1))
                                fx_spks_all[l_idx].extend(data[:, l_idx, 500:1000].sum(axis=1))

                # 3. Gather Stimulus (p1) vs Baseline data
                # Using RRRR p1 as gold standard for S+
                p1_spks = rrrr_data[:, :, 1000:1531].sum(axis=2)
                p1_fx_spks = rrrr_data[:, :, 500:1000].sum(axis=2)

                for _, row in units_in_probe.iterrows():
                    l_idx = row['local_idx']
                    if l_idx >= rrrr_data.shape[1]: continue
                    
                    # Stability
                    is_stable = (row['isi_violations'] < 0.5) and rrrr_stable[l_idx]
                    
                    # S+ / S- Test (RRRR p1 vs fx)
                    _, p_s = ttest_rel(p1_spks[:, l_idx], p1_fx_spks[:, l_idx])
                    mean_p1 = p1_spks[:, l_idx].mean()
                    mean_sfx = p1_fx_spks[:, l_idx].mean()
                    is_s_plus = (p_s < BONFERRONI_ALPHA) and (mean_p1 > mean_sfx)
                    is_s_minus = (p_s < BONFERRONI_ALPHA) and (mean_p1 < mean_sfx)
                    
                    # O+ / O- Test (Pooled Omission vs pooled fx)
                    is_o_plus = False
                    is_o_minus = False
                    if len(omit_spks_all[l_idx]) > 0:
                        _, p_o = ttest_rel(omit_spks_all[l_idx], fx_spks_all[l_idx])
                        mean_o = np.mean(omit_spks_all[l_idx])
                        mean_ofx = np.mean(fx_spks_all[l_idx])
                        is_o_plus = (p_o < BONFERRONI_ALPHA) and (mean_o > mean_ofx)
                        is_o_minus = (p_o < BONFERRONI_ALPHA) and (mean_o < mean_ofx)

                    results.append({
                        'session_id': session, 'unit_id': row['unit_id_in_session'],
                        'area': row['location'], 'is_stable_ultimate': is_stable,
                        'is_s_plus': is_s_plus, 'is_s_minus': is_s_minus,
                        'is_o_plus': is_o_plus, 'is_o_minus': is_o_minus,
                        'p_omit': p_o if len(omit_spks_all[l_idx]) > 0 else 1.0
                    })
            except Exception as e:
                continue

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Stringent categorization saved. O+ Count: {results_df['is_o_plus'].sum()}")

if __name__ == "__main__":
    perform_stringent_audit()
