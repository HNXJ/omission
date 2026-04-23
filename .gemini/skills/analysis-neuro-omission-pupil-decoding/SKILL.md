---
name: analysis-neuro-omission-pupil-decoding
---
# analysis-neuro-omission-pupil-decoding

## Purpose
Decodes stimulus identity and omission surprise from pupillometry. Maps pupil diameter shifts to arousal and cognitive load via SVM classification.

## Input
| Name | Type | Description |
|------|------|-------------|
| pupil_raw | ndarray(trials, T) | Raw pupil diameter |
| blink_mask | ndarray(trials, T) | Boolean blink timestamps |
| trial_labels | ndarray(trials,) | Condition/identity labels |
| cv_folds | int | Cross-validation folds (default: 5) |

## Output
| Name | Type | Description |
|------|------|-------------|
| accuracy_trace | ndarray(T,) | Time-resolved classification performance |
| surprise_metric | float | Peak dilation amplitude in omission window |

## Example
```python
from src.analysis.pupillometry import decode_pupil_identity
accuracy = decode_pupil_identity(pupil_data, labels, cv=5)
print(f"""[result] Max decoding accuracy: {max(accuracy):.2%}""")
```

## Files
- [pupil_decoding.py](file:///D:/drive/omission/src/analysis/pupil_decoding.py) — Core implementation
