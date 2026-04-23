---
name: analysis-global-unit-counts-nwb
---
# analysis-global-unit-counts-nwb

## Purpose
Audits NWB files to report total neural units per brain area across all sessions. Essential for verifying data coverage before cross-area analyses.

## Input
| Name | Type | Description |
|------|------|-------------|
| data_dir | str | Path to directory containing `.nwb` files |
| TARGET_AREAS | list[str] | Brain regions to count (e.g. `['V1', 'PFC', 'FEF']`) |
| AREA_MAPPING | dict | Normalization map (e.g. `{'DP': 'V4'}`) |

## Output
| Name | Type | Description |
|------|------|-------------|
| counts | dict[str, int] | Global unit count per area |

## Example
```python
from collections import defaultdict
from pynwb import NWBHDF5IO
import os

counts = defaultdict(int)
for f in [f for f in os.listdir(data_dir) if f.endswith('.nwb')]:
    with NWBHDF5IO(os.path.join(data_dir, f), 'r') as io:
        nwb = io.read()
        for idx, unit in nwb.units.to_dataframe().iterrows():
            loc = nwb.electrodes[int(unit['peak_channel_id']), 'location']
            if loc in ['V1', 'PFC']:
                counts[loc] += 1
print(f"""[result] {dict(counts)}""")
```

## Files
- [nwb-analysis](file:///D:/drive/omission/.gemini/skills/nwb-analysis/SKILL.md) — Broader NWB skill