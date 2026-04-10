
import pandas as pd
import numpy as np
import re
from pathlib import Path
from scipy.stats import ttest_rel

# Paths
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')
REFINED_PATH = Path(r'D:\drive\omission\outputs\unit_refined_categories_v3.csv') # The 9 O+ units
AUDIT_PATH = Path(r'D:\drive\omission\outputs\unit_refined_categories_v2.csv') # All units refined audit

def generate_detailed_audit():
    # Load data
    df = pd.read_csv(PROFILE_PATH, low_memory=False)
    refined_o_plus = pd.read_csv(REFINED_PATH)
    full_audit = pd.read_csv(AUDIT_PATH)

    # 1. Clean merge full audit into profile
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None
    df['ses_tmp'] = df['session_nwb'].apply(extract_ses)
    df['refined_key'] = df['ses_tmp'] + "_" + df['unit_id_in_session'].astype(str)
    
    full_audit['refined_key'] = full_audit['session_id'].astype(str) + "_" + full_audit['unit_id'].astype(str)
    
    df = pd.merge(df, full_audit.drop(columns=['session_id', 'unit_id', 'area']), on='refined_key', how='left')

    # 2. Area Mapping
    def map_area(row):
        loc = str(row['location'])
        ch_local = row['peak_channel_id'] % 128
        if ',' in loc:
            parts = [p.strip() for p in loc.split(',')]
            if len(parts) == 2: return parts[0] if ch_local < 64 else parts[1]
            elif len(parts) == 3:
                if ch_local < 42: return parts[0]
                elif ch_local < 84: return parts[1]
                else: return parts[2]
        return 'V4' if loc == 'DP' else loc

    df['area_hier'] = df.apply(map_area, axis=1)
    CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    df_hier = df[df['area_hier'].isin(CANONICAL_AREAS)].copy()

    # 3. Population Stats Table
    area_groups = df_hier.groupby('area_hier')
    pop_stats = area_groups.agg({
        'is_stable_ultimate': 'sum',
        'is_s_plus': 'sum',
        'is_s_minus': 'sum',
        'is_o_plus': 'sum',
        'is_o_minus': 'sum'
    }).rename(columns={
        'is_stable_ultimate': 'Ultimate_Stable',
        'is_s_plus': 'S+', 'is_s_minus': 'S-',
        'is_o_plus': 'O+', 'is_o_minus': 'O-'
    })
    pop_stats['Total'] = area_groups.size()
    pop_stats = pop_stats.reindex(CANONICAL_AREAS).fillna(0).astype(int)

    # 4. Detailed O+ Table (The "Final 9")
    refined_o_plus['refined_key'] = refined_o_plus['session_id'].astype(str) + "_" + refined_o_plus['unit_id'].astype(str)
    o_plus_keys = refined_o_plus['refined_key']
    detailed_o_plus = df_hier[df_hier['refined_key'].isin(o_plus_keys)].copy()
    
    # 5. Build Markdown
    doc = "# Detailed Population Audit & Omission Neuron Census\n\n"
    
    doc += "## 1. Population Statistics (All 11 Areas)\n"
    doc += "*Criteria*: \n"
    doc += "- **Ultimate Stable**: ISI < 0.5 AND min 1Hz firing in EVERY RRRR trial.\n"
    doc += "- **S+/S-**: Sig vs Fixation (Bonferroni corrected $p < 8.2e-6$).\n"
    doc += "- **O+/O-**: Sig vs Fixation AND Sig vs Delay (Bonferroni corrected).\n\n"
    doc += pop_stats.to_markdown() + "\n\n"

    doc += "## 2. Census of Significant Omission Neurons (O+)\n"
    doc += "*The following 9 units passed the highest stringency filters ($p < 8.2 \\times 10^{-6}$ and Effect Ratio $> 2.0$).*\n\n"
    
    # session_id and unit_id are from full_audit, so let's use refined_key parts
    detailed_o_plus['Session'] = detailed_o_plus['ses_tmp']
    detailed_o_plus['Unit'] = detailed_o_plus['unit_id_in_session']
    detailed_cols = ['Session', 'Unit', 'area_hier', 'snr', 'presence_ratio', 'p_omit']
    doc += detailed_o_plus[detailed_cols].to_markdown(index=False) + "\n\n"

    doc += "## 3. Statistical Test Methodology\n"
    doc += "### a. Stability Constraint\n"
    doc += "- ISI violations < 0.5%.\n"
    doc += "- Continuous monitoring: Average firing rate must exceed 1.0 Hz in every single individual trial of the RRRR condition.\n\n"
    
    doc += "### b. Polarity Significance (S+ / O+)\n"
    doc += "- **Test**: Two-sided Related Samples T-Test (ttest_rel).\n"
    doc += "- **Baseline**: 500ms Fixation period (fx) immediately preceding the first presentation of the sequence.\n"
    doc += "- **Alpha Correction**: Bonferroni family-wise error rate correction applied across the total population of 6,040 units.\n"
    doc += "  - Base $\\alpha = 0.05$\n"
    doc += "  - Corrected $\\alpha \\approx 8.278 \\times 10^{-6}$.\n"
    doc += "- **Omission Local Baseline**: Omission windows must also be significantly higher ($p < 0.05$) than the 500ms **Delay Baseline** immediately preceding the omission slot to filter out simple ramp-up or drift effects.\n"

    with open(r'D:\drive\omission\outputs\detailed_population_audit.md', 'w') as f:
        f.write(doc)
    print("Detailed audit generated.")

if __name__ == "__main__":
    generate_detailed_audit()
