---
name: analysis-neuro-omission-oculomotor-suite
---
# analysis-neuro-omission-oculomotor-suite

## Purpose
Detects saccades/microsaccades, validates fixation stability, and generates pupillometric correlates of attention during visual omissions.

## Input
| Name | Type | Description |
|------|------|-------------|
| eye_data | ndarray(2, T) | Raw XY in DVA from `.bhv2.mat` |
| fs | float | 1000 Hz |
| screen_dist | float | 57 cm |
| vel_thresh | float | 30 DVA/s for saccade detection |

## Output
| Name | Type | Description |
|------|------|-------------|
| saccade_events | list[dict] | `{time, amplitude, velocity, direction}` |
| microsaccades | list[dict] | Subset with amplitude < 1.5° |
| pupil_trace | ndarray(T,) | Normalized pupillometry |

## Example
```python
from src.analysis.oculomotor import detect_saccades
eye_x, eye_y = get_calibrated_eye_data(session_id)
saccades = detect_saccades(eye_x, eye_y, fs=1000, thresh=30)
microsaccades = [s for s in saccades if s.amplitude < 1.5]
print(f"""[result] {len(microsaccades)} microsaccades""")
```

## Files
- [EyeDataMapper.py](file:///D:/drive/omission/src/utils/EyeDataMapper.py) — NWB-BHV correlator
