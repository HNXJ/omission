---
name: analysis-behavioral-data-processing
description: Provides foundational utilities for processing raw MonkeyLogic behavioral .mat files and extracted behavioral data (eye, pupil, event codes). Includes functions for data loading, trial-wise feature extraction, saccade detection, and eye movement direction calculation.
---
# skill: analysis-behavioral-data-processing

## When to Use
Use this skill when processing raw behavioral data from MonkeyLogic (stored in `.mat` files) or when analyzing eye-tracking and pupilometry data. It provides the low-level functions required for:
- Loading legacy MonkeyLogic structures.
- Extracting synchronized eye position and pupil diameter.
- Detecting behavioral events (saccades, microsaccades).
- Calculating angular directions of eye movements.

## What is Input
- **`file_path`**: `str` - Path to the MonkeyLogic `.mat` behavioral file.
- **`trial_struct`**: `dict`/`SimpleNamespace` - Individual trial data structure.
- **`eye_x`, `eye_y`**: `numpy.ndarray` - 1D arrays of eye coordinates.
- **`fs`**: `float` - Sampling frequency (default: 1000 Hz).
- **`vel_thresh`, `amp_thresh`**: `float` - Thresholds for saccade detection logic.

## What is Output
- **`eye`, `pupil`**: `numpy.ndarray` - Extracted and conditioned time-series data.
- **`codes`, `times`**: `numpy.ndarray` - Behavioral event codes and their corresponding timestamps.
- **`saccade_indices`**: `numpy.ndarray` - Time points (indices) where saccades were detected.
- **`angles`**: `numpy.ndarray` - Angular directions in degrees (0-360).

## Algorithm / Methodology
1. **Data Parsing**: Uses `scipy.io.loadmat` to navigate complex MonkeyLogic nested structures.
2. **Feature Extraction**: Extracts `AnalogData` (Eye/Pupil) and `BehavioralCodes` (Event timestamps).
3. **Saccade Detection**: Employs a velocity-threshold algorithm. Velocity is calculated as the magnitude of the coordinate gradients scaled by sampling rate.
4. **Angular Calculation**: Uses `arctan2` on coordinate differentials (`diff`) to determine the vector direction of eye movements, normalized to 0-360 degrees.

## Placeholder Example
```python
from codes.functions.behavioral_utils import load_behavioral_data, extract_trial_data, detect_saccades

# 1. Load the raw behavioral file
bhv_data = load_behavioral_data("data/session_A.mat")

# 2. Extract data for trial #5
eye, pupil, codes, times = extract_trial_data(bhv_data[5])

# 3. Detect saccades in this trial
saccade_idx, velocities = detect_saccades(eye[0], eye[1], fs=1000)
print(f"Trial 5: {len(saccade_idx)} saccades detected.")
```

## Relevant Context / Files
- [behavioral_utils.py](file:///D:/drive/omission/codes/functions/behavioral_utils.py) — Core implementation.
- [EyeDataMapper](file:///D:/drive/omission/src/utils/eye_data_mapper.py) — Related NWB correlation tool.