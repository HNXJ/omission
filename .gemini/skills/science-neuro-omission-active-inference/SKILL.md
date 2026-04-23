---
name: science-neuro-omission-active-inference
---
# science-neuro-omission-active-inference

## Purpose
Interprets neural results through Active Inference and Free-Energy minimization. Maps transients to variational updates, calculates surprisal, dissociates complexity vs accuracy.

## Key Formulas
| Concept | Formula | Value |
|---------|---------|-------|
| Surprisal | `-log₂(p)` | 10% event → 3.32 bits |
| Standard event | `-log₂(0.7)` | 0.51 bits |
| Free Energy | `F = -log p(o) + KL[q(s) \|\| p(s\|o)]` | — |

## Core Logic
1. Brain maintains posterior `p(s|o)` predicting next stimulus in AAAB sequence
2. Omissions (AXAB) create expectation-input mismatch
3. Surprise signal = brain updating `q(s)` to minimize F
4. High-order areas (PFC/FEF) lead sensory areas during omissions

## Example
```python
import numpy as np
def surprisal(p): return -np.log2(p)
print(f"""[result] Standard: {surprisal(0.7):.2f} bits, Omission: {surprisal(0.1):.2f} bits""")
```

## Files
- [information_theory.py](file:///D:/drive/omission/src/math/information_theory.py) — Surprisal/entropy
