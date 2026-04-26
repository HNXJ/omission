---
name: science-neuro-omission-prediction-errors
---
# science-neuro-omission-prediction-errors

## Purpose
Quantifies surprise (prediction error) transients during sequence violations. Tests deviance-scaling proportionality and identifies detection hubs.

## Input
| Name | Type | Description |
|------|------|-------------|
| omit_psth | ndarray(T,) | Trial-averaged PSTH for omission condition |
| std_psth | ndarray(T,) | Trial-averaged PSTH for standard condition |
| surprisal_bits | float | Information content of the event |

## Output
| Name | Type | Description |
|------|------|-------------|
| surprise_index | float | `(omit - std) / (omit + std + ε)` — >0 = enhancement |
| scaling_slope | float | Linear fit of neural magnitude vs surprisal |
| detection_hub | str | Earliest area crossing Z>3 threshold |

## Example
```python
import numpy as np
def surprise_index(omit_rate, std_rate):
    return (omit_rate - std_rate) / (omit_rate + std_rate + 1e-6)
idx = surprise_index(rate_p4_omit, rate_p4_std)
print(f"""[result] Surprise index: {idx:.3f}""")
```

## Files
- [surprise_scaling.py](file:///D:/drive/omission/src/math/surprise_scaling.py) — Regression engine
