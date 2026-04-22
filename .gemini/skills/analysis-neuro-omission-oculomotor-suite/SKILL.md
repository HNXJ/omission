---
name: analysis-neuro-omission-oculomotor-suite
description: Pipeline for analyzing saccades, microsaccades, and pupillometry. Maps eye movements to attention and internal states during visual omissions.
---
# skill: analysis-neuro-omission-oculomotor-suite

## When to Use
Use this skill to validate fixation stability and analyze behavioral correlates of attention. It is crucial for:
- Detecting microsaccades as a proxy for covert attention.
- Auditing fixation errors (TrialError != 0).
- Correlating pupil dilation with omission-induced arousal.
- Mapping eye movement directionality relative to stimulus orientation.

## What is Input
- **Eye Data**: Raw X/Y coordinates from eye-tracking (e.g., `.bhv2.mat`).
- **Calibration**: Screen distance (57cm) and sampling rate (1000Hz).
- **Events**: Stimulus onset/offset timestamps.

## What is Output
- **Saccade Events**: Timestamps, amplitudes, and velocities of detected eye movements.
- **Pupil Traces**: Normalized pupillometry traces.
- **Figures**: Rose plots for directionality and time-resolved velocity plots.

## Algorithm / Methodology
1. **Calibration**: Converts raw eye signals into Degrees of Visual Angle (DVA).
2. **Velocity Thresholding**: Detects saccades where velocity > 30 DVA/s and amplitude > 1.5°.
3. **Microsaccade Extraction**: Identifies small movements (<1.5°) using the Engbert-Kliegl algorithm.
4. **Rose Plot Generation**: Binning eye movement directions to test for biases toward stimulus orientation (45° vs. 135°).
5. **Syncing**: Aligning all traces to photodiode-verified stimulus onsets.

## Placeholder Example
```python
import numpy as np
from src.analysis.oculomotor import detect_saccades

# 1. Prepare eye traces (X, Y in DVA)
eye_x, eye_y = get_calibrated_eye_data(session_id)

# 2. Detect events
saccades = detect_saccades(eye_x, eye_y, fs=1000, thresh=30)

# 3. Filter for microsaccades
microsaccades = [s for s in saccades if s.amplitude < 1.5]
print(f"Detected {len(microsaccades)} microsaccades in this session.")
```

## Relevant Context / Files
- [analysis-behavioral-data-processing](file:///D:/drive/omission/.gemini/skills/analysis-behavioral-data-processing/skill.md) — For data loading logic.
- [EyeDataMapper.py](file:///D:/drive/omission/src/utils/EyeDataMapper.py) — For NWB-Behavioral correlation.
