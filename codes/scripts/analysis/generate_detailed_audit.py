
import pandas as pd
import numpy as np
import re
from pathlib import Path

# Paths
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')
AUDIT_PATH = Path(r'D:\drive\omission\outputs\unit_refined_categories_v2.csv') 
RATIO_PATH = Path(r'D:\drive\omission\outputs\omission_ratio_groups.csv')

def generate_detailed_audit():
    # Load data
    df = pd.read_csv(PROFILE_PATH, low_memory=False)
    full_audit = pd.read_csv(AUDIT_PATH)
    ratio_df = pd.read_csv(RATIO_PATH)

    # 1. Clean merge full audit into profile
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None
    df['ses_tmp'] = df['session_nwb'].apply(extract_ses)
    df['refined_key'] = df['ses_tmp'] + "_" + df['unit_id_in_session'].astype(str)
    
    full_audit['refined_key'] = full_audit['session_id'].astype(str) + "_" + full_audit['unit_id'].astype(str)
    ratio_df['refined_key'] = ratio_df['session'].astype(str) + "_" + ratio_df['unit_id'].astype(str)
    
    # Merge Audit
    df = pd.merge(df, full_audit.drop(columns=['session_id', 'unit_id', 'area']), on='refined_key', how='left')
    
    # Merge Ratio Brackets
    df = pd.merge(df, ratio_df[['refined_key', 'bracket', 'ratio']], on='refined_key', how='left')

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

    # 3. Build Markdown
    doc = "# Detailed Population Audit & Omission Neuron Census\n\n"
    
    # Statistics Table
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

    doc += "## 1. Population Statistics (All 11 Areas)\n"
    doc += "*Criteria*: \n"
    doc += "- **Ultimate Stable**: ISI < 0.5 AND min 1Hz firing in EVERY RRRR trial.\n"
    doc += "- **S+/S-**: Sig vs Fixation (Bonferroni corrected $p < 8.2e-6$).\n"
    doc += "- **O+/O-**: Sig vs Fixation AND Sig vs Delay (Bonferroni corrected).\n\n"
    doc += pop_stats.to_markdown() + "\n\n"

    # Census Sections
    detailed_cols = ['Session', 'Unit', 'area_hier', 'snr', 'presence_ratio', 'ratio', 'p_omit']
    df_hier['Session'] = df_hier['ses_tmp']
    df_hier['Unit'] = df_hier['unit_id_in_session']

    brackets = [
        ("2.0+", "Tier 1: High Magnitude Omission Neurons"),
        ("1.75-2.0", "Tier 2: Robust Omission Neurons"),
        ("1.5-1.75", "Tier 3: Moderate Omission Neurons"),
        ("1.25-1.5", "Tier 4: Subtle Omission Neurons")
    ]

    for b_code, b_name in brackets:
        doc += f"## {b_name} ({b_code})\n"
        b_units = df_hier[df_hier['bracket'] == b_code].sort_values('ratio', ascending=False)
        if b_units.empty:
            doc += "*No units in this bracket pass the strict significance filters.*\n\n"
        else:
            doc += b_units[detailed_cols].to_markdown(index=False) + "\n\n"

    # Methodology
    doc += "## 3. Statistical Test Methodology\n"
    doc += "### a. Stability Constraint\n"
    doc += "- ISI violations < 0.5%.\n"
    doc += "- Continuous monitoring: Average firing rate must exceed 1.0 Hz in every single individual trial of the RRRR condition.\n\n"
    doc += "### b. Polarity Significance (S+ / O+)\n"
    doc += "- **Test**: Two-sided Related Samples T-Test (ttest_rel).\n"
    doc += "- **Alpha Correction**: Bonferroni family-wise correction ($p < 8.278 \\times 10^{-6}$).\n"

    with open(r'D:\drive\omission\outputs\detailed_population_audit.md', 'w') as f:
        f.write(doc)
    print("Detailed multi-tier audit generated.")

if __name__ == "__main__":
    generate_detailed_audit()
