---
name: analysis-nwb-read-guardrails
description: Mandatory performance and safety protocols for NWB access. Enforces lazy-loading, context-preservation, and memory-efficient data extraction.
---
# skill: analysis-nwb-read-guardrails

## When to Use
Use this skill whenever opening or processing NWB files. It is mandatory for:
- Preventing memory overflows when reading high-density LFP (128+ channels).
- Avoiding "Closed File" errors by maintaining proper `NWBHDF5IO` context.
- Optimizing trial-loop execution by pre-loading static metadata (e.g., channel maps).
- Ensuring source data integrity by strictly enforcing read-only access.

## What is Input
- **NWB Path**: File system path to the target session.
- **Access Pattern**: Definition of the requested data slice (e.g., units vs. LFP).

## What is Output
- **IO Context**: A managed `NWBHDF5IO` object or a data-safe copy.
- **Lazy Objects**: Pointers to on-disk datasets (not materialized arrays).
- **Static Caches**: Precomputed dictionaries for channel-to-area mappings.

## Algorithm / Methodology
1. **Context Management**: Always use `with NWBHDF5IO(path, 'r') as io:` to ensure files are closed properly, OR pass the `nwb` object explicitly through the pipeline.
2. **Lazy Slicing**: Never call `series.data[:]`. Always use windowed slicing `series.data[start:end, channels]` to keep memory usage proportional to the analysis window.
3. **Pre-Indexing**: Extracts the `electrodes` and `units` tables once at the start of a session and caches them as DataFrames for fast lookup.
4. **Sanitization**: Applies `np.nan_to_num` only to the *extracted* slice, never the full dataset.
5. **Garbage Collection**: Explicitly calls `gc.collect()` after processing each session to free up HDF5 buffers.

## Placeholder Example
```python
from pynwb import NWBHDF5IO
import gc

def process_session(path):
    with NWBHDF5IO(path, 'r', load_namespaces=True) as io:
        nwb = io.read()
        # 1. Pre-load unit metadata
        units_df = nwb.units.to_dataframe()
        
        # 2. Slice LFP lazily
        lfp_slice = nwb.acquisition['LFP'].data[0:1000, 0:10]
        
        # 3. Process...
        print(f"Read {lfp_slice.shape} samples safely.")
    
    gc.collect() # Mandatory cleanup
```

## Relevant Context / Files
- [analysis-nwb-data-availability-report](file:///D:/drive/omission/.gemini/skills/analysis-nwb-data-availability-report/skill.md) — For auditing files before reading.
- [src/utils/nwb_io.py](file:///D:/drive/omission/src/utils/nwb_io.py) — Reference implementation of these guardrails.
