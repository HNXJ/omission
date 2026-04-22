---
name: coding-neuro-omission-behavioral-utils
description: Low-level utilities for parsing and normalizing oculomotor (DVA, Pupil) and trial metadata from raw BHV2 files.
---
# skill: coding-neuro-omission-behavioral-utils

## When to Use
Use this skill when developing or debugging the behavioral data ingestion pipeline. It is critical for:
- Converting raw voltage/pixel eye coordinates from BHV2 into Degrees of Visual Angle (DVA).
- Extracting trial-level event codes (e.g., Code 101 for Stimulus Onset).
- Normalizing pupil diameter to baseline arousal levels.
- Handling trial-rejection logic based on fixation breaks or blink artifacts.

## What is Input
- **BHV2.mat Files**: Raw output from MonkeyLogic or similar behavioral control systems.
- **Eye Calibration Maps**: Gain and offset parameters for XY-to-DVA conversion.
- **Trial Metadata**: Condition IDs, stimulus identity (A/B), and timing offsets.

## What is Output
- **Cleaned Behavioral Arrays**: `.npy` files containing synchronized EyeX, EyeY, and Pupil traces.
- **Event Tables**: `.csv` or `.json` files mapping trial indices to event timestamps.
- **QC Metrics**: Fixation stability scores and blink-density reports.

## Algorithm / Methodology
1. **BHV Parsing**: Uses a specialized MATLAB-to-Python bridge to extract nested analog data from BHV2 structures.
2. **DVA Transformation**: Applies the standard project gain formula: `DVA = (Voltage - Offset) * Gain`.
3. **Synchronization**: Aligns behavioral clock-times with the LFP/Spike neural clock using "Sync Pulse" cross-correlation.
4. **Saccade Detection**: Implements the Engbert & Kliegl velocity threshold algorithm (>30 deg/s) to isolate eye movements.
5. **Baseline Correction**: Subtracts the mean pupil diameter during the fixation period (-200ms to 0ms) from the task-related trace.

## Placeholder Example
```python
from src.utils.behavioral import bhv_to_dva, detect_saccades

# 1. Convert raw eye data to DVA
eye_dva = bhv_to_dva(raw_eye_data, gain=2.5, offset=0.1)

# 2. Detect saccadic events
saccades = detect_saccades(eye_dva, threshold=30)
print(f"Detected {len(saccades)} saccades in trial.")
```

## Relevant Context / Files
- [coding-neuro-omission-bhv-parser](file:///D:/drive/omission/.gemini/skills/coding-neuro-omission-bhv-parser/skill.md) — For raw binary file handling.
- [src/utils/eye_data_mapper.py](file:///D:/drive/omission/src/utils/eye_data_mapper.py) — The canonical 1:1 NWB-BHV correlator.
