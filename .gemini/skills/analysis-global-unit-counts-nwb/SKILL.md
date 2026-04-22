---
name: analysis-global-unit-counts-nwb
description: Audits Neurodata Without Borders (NWB) files to calculate and report the total number of recorded neural units assigned to predefined target brain areas across all sessions. This provides a global overview of the neural data coverage per brain region.
---
# skill: analysis-global-unit-counts-nwb

## When to Use
Use this skill when you need a high-level audit of the total neural units available across the entire dataset. It is essential for:
- Verifying data coverage for specific brain regions (e.g., V1, PFC).
- Determining if there are enough units for cross-area population analyses.
- Validating the NWB conversion and electrode-to-area mapping consistency.

## What is Input
- **`data_dir`**: `str` - Path to the directory containing NWB files.
- **`TARGET_AREAS`**: `list` - List of brain regions to count (e.g., `['V1', 'PFC', 'FEF']`).
- **`AREA_MAPPING`**: `dict` - Dictionary for normalizing region names (e.g., `{'DP': 'V4'}`).

## What is Output
- **Console Report**: A printed summary of the global unit count per area across all sessions.
- **Aggregation Logic**: Internal sum of units where `electrode.location` matches `TARGET_AREAS`.

## Algorithm / Methodology
1. **File Scanning**: Recursively finds all `.nwb` files in the target directory.
2. **NWB Inspection**: Opens each NWB file using `PyNWB` and accesses the `units` and `electrodes` tables.
3. **Spatial Mapping**:
   - Retrieves the `peak_channel_id` for each unit.
   - Maps this channel back to the `electrodes` table to find the assigned brain region (`location`).
4. **Area Normalization**: Applies `AREA_MAPPING` to handle synonymous or sub-region labels.
5. **Summation**: Aggregates counts into a global dictionary and displays the result.

## Placeholder Example
```python
import os
from pynwb import NWBHDF5IO
from collections import defaultdict

data_dir = 'D:/drive/omission/data/'
counts = defaultdict(int)
target_areas = ['V1', 'PFC', 'MT']

# 1. Iterate over sessions
for f in [f for f in os.listdir(data_dir) if f.endswith('.nwb')]:
    with NWBHDF5IO(os.path.join(data_dir, f), 'r') as io:
        nwb = io.read()
        units_df = nwb.units.to_dataframe()
        
        # 2. Count units by location
        for idx, unit in units_df.iterrows():
            loc = nwb.electrodes[int(unit['peak_channel_id']), 'location']
            if loc in target_areas:
                counts[loc] += 1

# 3. Report
print("Global Data Audit:")
for area, count in counts.items():
    print(f"{area}: {count} units")
```

## Relevant Context / Files
- [NWB Standard](https://www.nwb.org/) — Schema for units and electrodes.
- [nwb-analysis](file:///D:/drive/omission/.gemini/skills/nwb-analysis/skill.md) — Broader NWB processing skill.