---
name: analysis-metadata-extraction
description: Extracts comprehensive trial metadata from Neurodata Without Borders (NWB) files and saves it into a CSV format for easy tabular analysis. This skill is useful for quickly accessing and manipulating trial-specific information such as start/stop times, conditions, and behavioral events.
---
# skill: analysis-metadata-extraction

## When to Use
Use this skill when you need a high-fidelity tabular view of trial parameters. It is ideal for:
- Auditing trial counts per condition (e.g., Omission vs. Standard).
- Cross-referencing neural data with behavioral timestamps.
- Creating input files for trial-level statistical modeling.

## What is Input
- **NWB File**: Path to the `.nwb` recording.
- **Table Targets**: Searches for `omission_glo_passive` or the generic `trials` table in `nwb.intervals`.
- **Output Dir**: Path where the resulting CSV will be stored.

## What is Output
- **Trial CSV**: A file named `ses-<ID>_trials.csv` containing all columns from the NWB intervals table (e.g., `start_time`, `stop_time`, `condition`).

## Algorithm / Methodology
1. **NWB Access**: Opens the NWB file and traverses the `intervals` module.
2. **Table Identification**: Implements a fallback logic (prioritizing custom Omission tables over generic NWB trials).
3. **Dataframe Conversion**: Serializes the `NWBTable` into a standard Pandas DataFrame.
4. **Persistence**: Saves to disk while ensuring no overwriting of existing metadata audits.

## Placeholder Example
```python
import pynwb
import pandas as pd

# 1. Access NWB trials
with pynwb.NWBHDF5IO('ses-230818.nwb', 'r') as io:
    nwb = io.read()
    intervals = nwb.intervals['omission_glo_passive']
    
    # 2. Extract to CSV
    df = intervals.to_dataframe()
    df.to_csv('metadata_audit.csv', index=False)

print(f"Extracted {len(df)} trials.")
```

## Relevant Context / Files
- [extract_trial_metadata.py](file:///D:/drive/omission/codes/scripts/extract_trial_metadata.py) — Source implementation.
- [analysis-behavioral-data-processing](file:///D:/drive/omission/.gemini/skills/analysis-behavioral-data-processing/skill.md) — Related behavioral context.