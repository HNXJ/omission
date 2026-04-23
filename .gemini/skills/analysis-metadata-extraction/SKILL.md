---
name: analysis-metadata-extraction
---
# analysis-metadata-extraction

## Purpose
Extracts NWB trial metadata (start/stop times, conditions, events) into CSV for tabular analysis and cross-referencing with neural data.

## Input
| Name | Type | Description |
|------|------|-------------|
| nwb_path | str | Path to `.nwb` recording |
| table_name | str | `omission_glo_passive` (preferred) or `trials` (fallback) |

## Output
| Name | Type | Description |
|------|------|-------------|
| trial_csv | str | Path to `ses-<ID>_trials.csv` with all interval columns |

## Example
```python
import pynwb, pandas as pd
with pynwb.NWBHDF5IO('ses-230818.nwb', 'r') as io:
    nwb = io.read()
    df = nwb.intervals['omission_glo_passive'].to_dataframe()
    df.to_csv('metadata_audit.csv', index=False)
    print(f"""[result] Extracted {len(df)} trials""")
```

## Files
- [extract_trial_metadata.py](file:///D:/drive/omission/codes/scripts/extract_trial_metadata.py) — Source