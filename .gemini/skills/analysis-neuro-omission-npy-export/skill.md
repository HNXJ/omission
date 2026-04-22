---
name: analysis-npy-export
description: High-performance pipeline for converting NWB sessions into chunked NumPy arrays. Handles LFP, spikes, and behavioral streams with precise trial alignment.
---
# skill: analysis-npy-export

## When to Use
Use this skill when preparing large-scale datasets for deep learning or custom analysis pipelines that require fast random access. It is ideal for:
- Exporting windowed LFP blocks (e.g., 6000 samples at 1kHz).
- Binarizing spike times into high-resolution occupancy matrices.
- Synchronizing eye-tracking and pupil data with neural events.
- Creating "condition-pure" subsets (e.g., all Omission trials) for across-session comparisons.

## What is Input
- **NWB Files**: Raw session data in `data/nwb/`.
- **Trial Masks**: Condition definitions (e.g., RRRR, RRXR) from `jnwb`.
- **Extraction Window**: Time range relative to stimulus onset (e.g., -1000ms to +5000ms).

## What is Output
- **.npy Arrays**: Compressed NumPy files in `data/arrays/` (Behavioral, LFP, Spikes).
- **Metadata Sidecars**: `.metadata.json` files containing sampling rates, channel maps, and trial counts.
- **Log Reports**: Summary of export success/failures per session.

## Algorithm / Methodology
1. **Indexing**: Parses the `omission_glo_passive` intervals and identifies Code 101.0 (p1 onset).
2. **Masking**: Filters trials based on the sequence history (e.g., isolating the omission in RRXR).
3. **Chunking**: Loads trials in manageable chunks (e.g., 32 trials) to minimize memory overhead.
4. **Slicing**: 
    - LFP/Behavioral: Linear indexing and Z-scoring.
    - Spikes: Pre-loads all spike times and populates a binary matrix `(n_trials, n_units, time_bins)`.
5. **Serialization**: Writes to disk using `np.save` with a standardized naming convention: `ses{id}-{stream}-{cond}.npy`.

## Placeholder Example
```python
from src.export.npy_pipeline import export_session_to_npy

# 1. Define export config
config = {
    'window': (-1.0, 5.0),
    'conditions': ['RRRR', 'RRXR'],
    'streams': ['lfp', 'spikes']
}

# 2. Execute export
export_session_to_npy('ses_001', config)

# 3. Verify on disk
import os
print(f"Exported files: {os.listdir('data/arrays/ses_001/')}")
```

## Relevant Context / Files
- [src/export/npy_io.py](file:///D:/drive/omission/src/export/npy_io.py) — Low-level NWB block reading logic.
- [src/export/npy_orchestrator.py](file:///D:/drive/omission/src/export/npy_orchestrator.py) — The main loop and file management.
