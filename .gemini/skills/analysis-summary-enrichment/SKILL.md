---
name: analysis-summary-enrichment
description: Tool for appending detailed NumPy array dimensional metadata (Trials, Channels, Samples) to the project data availability reports.
---
# skill: analysis-summary-enrichment

## When to Use
Use this skill after generating the base data availability report to provide granular structural metadata. It is the preferred method for:
- Verifying the consistency of array shapes (e.g., ensuring all sessions have 128 LFP channels).
- Identifying missing data chunks (e.g., probe1 present but probe2 empty).
- Providing "Single Source of Truth" dimensions for downstream modeling and feature extraction.
- Auditing trial counts and sampling rates across heterogeneous recording sessions.

## What is Input
- **Existing Summary**: `DATA_AVAILABILITY_SUMMARY.md` from the workspace root.
- **Processed Arrays**: `.npy` files in `data/arrays/` (Behavioral, LFP, Spikes).
- **Session IDs**: Extracted from filenames in `data/nwb/`.

## What is Output
- **Enriched Markdown**: An updated `DATA_AVAILABILITY_SUMMARY.md` with a "Detailed Array Shapes" table.
- **Shape Catalog**: A structured mapping of `(Session, Probe, Type) -> (Trials, Units/Chans, Samples)`.

## Algorithm / Methodology
1. **Session Parsing**: Extracts unique session IDs from the `sub-<ID>_ses-<ID>_rec.nwb` naming pattern.
2. **Representative Condition**: Selects "AAAB" as the canonical condition to check for shape consistency across all sessions.
3. **NumPy Inspection**: Loads `.npy` headers (using `mmap_mode='r'` for speed) to extract shape attributes without loading the full data.
4. **Markdown Insertion**: Identifies the "Detailed Array Shapes" heading in the summary file and overwrites the existing table with new data.
5. **Probe Aggregation**: Concatenates results from Probes 0, 1, and 2 into a single-row entry per session for scannability.

## Placeholder Example
```python
import pandas as pd
from src.utils.reporting import enrich_data_summary

# 1. Update the availability report with array shapes
enrich_data_summary(summary_path="DATA_AVAILABILITY_SUMMARY.md")

# 2. Resulting table in Markdown:
# | Session | Behavioral [T, 4, S] | LFP Probes [T, 128, S] | Unit Probes [T, N, S] |
# |:--------|:---------------------|:-----------------------|:----------------------|
# | 230629  | (100, 4, 10000)      | P0: (100, 128, 10000)  | P0: (100, 50, 10000)  |
```

## Relevant Context / Files
- [analysis-nwb-data-availability-report](file:///D:/drive/omission/.gemini/skills/analysis-nwb-data-availability-report/skill.md) — The base report generator.
- [src/extract/report_utils.py](file:///D:/drive/omission/src/extract/report_utils.py) — Implementation of enrichment logic.