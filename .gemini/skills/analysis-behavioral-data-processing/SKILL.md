---
name: analysis-behavioral-data-processing
---
# analysis-behavioral-data-processing

## Purpose
Loads MonkeyLogic `.mat` behavioral files, extracts eye/pupil traces, detects saccades, and computes angular directions. Absorbs `coding-neuro-omission-behavioral-utils`.

## Input
| Name | Type | Description |
|------|------|-------------|
| file_path | str | Path to `.bhv2.mat` file |
| trial_struct | dict | Individual trial data structure from MonkeyLogic |
| eye_x, eye_y | ndarray(N,) | Raw eye coordinates |
| fs | float | Sampling frequency (default: 1000 Hz) |
| vel_thresh | float | Velocity threshold for saccade detection (default: 30 deg/s) |

## Output
| Name | Type | Description |
|------|------|-------------|
| eye | ndarray(2, T) | Calibrated XY eye traces in DVA |
| pupil | ndarray(T,) | Normalized pupil diameter |
| saccade_indices | ndarray | Timepoints where saccades detected |
| angles | ndarray | Movement directions (0-360°) |

## Example
```python
from codes.functions.behavioral_utils import load_behavioral_data, detect_saccades
bhv = load_behavioral_data("data/session_A.mat")
eye, pupil, codes, times = extract_trial_data(bhv[5])
saccade_idx, _ = detect_saccades(eye[0], eye[1], fs=1000)
print(f"""[result] Trial 5: {len(saccade_idx)} saccades""")
```

## Files
- [behavioral_utils.py](file:///D:/drive/omission/codes/functions/behavioral_utils.py) — Core implementation
- [EyeDataMapper.py](file:///D:/drive/omission/src/utils/eye_data_mapper.py) — NWB-BHV correlator