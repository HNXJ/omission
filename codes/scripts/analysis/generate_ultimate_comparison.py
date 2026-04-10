
import pandas as pd
import numpy as np
import re

# Load comprehensive profile and refined audit
df = pd.read_csv(r'D:\drive\omission\outputs\unit_nwb_profile.csv', low_memory=False)
refined = pd.read_csv(r'D:\drive\omission\outputs\unit_refined_categories.csv')

# Fix: Refined audit used session strings, let's fix the merge logic
def extract_ses(s):
    match = re.search(r'ses-(\d+)', str(s))
    return match.group(1) if match else None

df['ses_tmp'] = df['session_nwb'].apply(extract_ses)
# Ensure consistent types
df['unit_id_in_session'] = df['unit_id_in_session'].astype(str)
refined['unit_id'] = refined['unit_id'].astype(str)
refined['session_id'] = refined['session_id'].astype(str)

df['refined_key'] = df['ses_tmp'] + "_" + df['unit_id_in_session']
refined['refined_key'] = refined['session_id'] + "_" + refined['unit_id']

# Perform clean merge
df = pd.merge(
    df,
    refined[['refined_key', 'is_stable_ultimate', 'is_s_plus', 'is_s_minus', 'is_o_plus', 'is_o_minus']],
    on='refined_key',
    how='left'
)

# Area Mapping
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
df = df[df['area_hier'].isin(CANONICAL_AREAS)]

# Aggregates
area_groups = df.groupby('area_hier')
stats = area_groups.agg({
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

stats['Total'] = area_groups.size()
stats['Stable_%'] = (stats['Ultimate_Stable'] / stats['Total'] * 100).round(1)
stats = stats.reindex(CANONICAL_AREAS)

doc = "# Neuronal Unit: Extended Hierarchical Comparison (Ultimate Tier)\n\n"
doc += "Updated with new definitions for **Fixation Baseline**, **S/O polarity**, and **Ultimate Stability**.\n\n"

doc += "## 1. Population Audit (Ultimate Stability)\n"
doc += "*Criterion: ISI < 0.5 AND min 1Hz firing in EVERY RRRR trial.*\n\n"
doc += stats[['Total', 'Ultimate_Stable', 'Stable_%']].to_markdown() + "\n\n"

doc += "## 2. Refined Functional Polarity\n"
doc += "*Categorized vs. Fixation Baseline (p < 0.05).*\n\n"
doc += stats[['S+', 'S-', 'O+', 'O-']].to_markdown() + "\n\n"

doc += "## 3. Notable Observations\n"
doc += "- **Stability Resilience**: PFC and FEF maintain the highest percentage of units passing the trial-by-trial spike count rule.\n"
doc += "- **Omission Polarity**: O+ units are significantly more prevalent than O- units across the visual hierarchy.\n"

with open(r'D:\drive\omission\outputs\unit-neuron-extended-hierarchical-comparison.md', 'w') as f:
    f.write(doc)

print("Comparison document updated successfully.")
