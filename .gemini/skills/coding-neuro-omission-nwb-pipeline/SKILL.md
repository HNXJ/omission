---
name: coding-neuro-omission-nwb-pipeline
description: Core orchestration layer for loading, aligning, and synchronizing large-scale neural data from the NWB repository.
---
# skill: coding-neuro-omission-nwb-pipeline

## When to Use
Use this skill when developing any analysis that requires loading neural signals. It is the absolute authority on:
- Navigating the `data/arrays/` and `data/nwb/` hierarchies.
- Synchronizing behavioral events with the 1kHz neural clock.
- Ensuring "Probe-Local" channel correctness (e.g., mapping Probe0 to V1 and Probe1 to PFC).
- Implementing memory-efficient data loading for multi-gigabyte LFP arrays.

## What is Input
- **Session IDs**: Canonical dates (e.g., `230629`).
- **Condition Keys**: `AAAB`, `AAAA`, `RRRR`, etc.
- **Modality Flags**: `LFP`, `Spikes`, `Pupil`.

## What is Output
- **Aligned Tensors**: 3D arrays `(trials, channels, samples)` or `(trials, units, samples)`.
- **Anatomical Metadata**: Mappings of channel indices to cortical layers and areas.
- **Latency Reports**: Verification of synchronization precision.

## Algorithm / Methodology
1. **Lazy Loading**: Uses `numpy.load(mmap_mode='r')` to prevent memory overflows during high-density LFP analysis.
2. **Temporal Alignment**: Anchors all trials to Code 101.0 (Onset of P1). Default window: -1000ms to +5000ms.
3. **Channel Mapping**: Consults the `NWB.Electrodes` table to resolve physical channel indices to area labels (V1, V2, PFC).
4. **Trial Concatenation**: Aggregates trials across multiple NWB files for a single session if necessary.
5. **Photodiode Verification**: Measures the V1 onset latency (expected 40-60ms) to ensure temporal offsets are correctly applied.

## Placeholder Example
```python
from src.extract.loader import load_aligned_session

# 1. Load aligned LFP data for V1
lfp_v1 = load_aligned_session(sid='230629', area='V1', modality='LFP', condition='AAAB')

# 2. Inspect the shape (trials, channels, time)
print(f"Loaded V1 LFP shape: {lfp_v1.shape}")
```

## Relevant Context / Files
- [analysis-nwb-data-availability-report](file:///D:/drive/omission/.gemini/skills/analysis-nwb-data-availability-report/skill.md) — For finding sessions.
- [src/extract/pipeline_orchestrator.py](file:///D:/drive/omission/src/extract/pipeline_orchestrator.py) — The main entry point for the loading pipeline.
