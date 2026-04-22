---
name: analysis-neuro-omission-pupil-decoding
description: Decodes stimulus identity and omission surprise from pupillometry signals. Maps pupil diameter shifts to arousal and cognitive load.
---
# skill: analysis-neuro-omission-pupil-decoding

## When to Use
Use this skill to analyze behavioral markers of surprise. It is particularly useful for:
- Decoding Stimulus A vs. Stimulus B from the slow pupillary response.
- Measuring the magnitude of "surprise" dilation during omission trials.
- Correlating pupil-based arousal with neural metrics (e.g., Gamma power).

## What is Input
- **Pupil Diameter**: Raw time-series from the eye-tracker.
- **Blink Masks**: Timestamps of blinks for interpolation/removal.
- **Trial Metadata**: Labels for stimulus identity and trial type (Standard vs. Omission).

## What is Output
- **Z-Scored Pupil Traces**: Baseline-corrected pupil diameter.
- **Decoding Accuracy**: SVM-based classification performance over time.
- **Surprise Metric**: Peak dilation amplitude during the omission window.

## Algorithm / Methodology
1. **Cleaning**: Interpolates across blinks and applies a low-pass filter (e.g., 10Hz) to remove high-frequency noise.
2. **Normalization**: Z-scores the diameter within each trial and subtracts the mean diameter of the pre-stimulus baseline.
3. **Feature Selection**: Extracts peak dilation, velocity of dilation, and area under the curve (AUC).
4. **Classification**: Trains a Support Vector Machine (SVM) on temporal windows to classify identity (A vs. B) or state (Standard vs. Omission).
5. **Cross-Validation**: Uses 5-fold cross-validation to ensure decoding robustness.

## Placeholder Example
```python
from src.analysis.pupillometry import decode_pupil_identity

# 1. Load cleaned pupil traces
pupil_data, labels = get_pupil_dataset(session_id)

# 2. Run decoder
accuracy_trace = decode_pupil_identity(pupil_data, labels, cv=5)

# 3. Check for peak decoding
print(f"Max identity decoding accuracy: {max(accuracy_trace):.2%}")
```

## Relevant Context / Files
- [analysis-neuro-omission-oculomotor-suite](file:///D:/drive/omission/.gemini/skills/analysis-neuro-omission-oculomotor-suite/skill.md) — For raw eye data processing.
- [src/analysis/pupil_decoding.py](file:///D:/drive/omission/src/analysis/pupil_decoding.py) — Core implementation.
