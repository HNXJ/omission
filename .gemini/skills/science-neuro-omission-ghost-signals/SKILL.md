---
name: science-neuro-omission-ghost-signals
---
# science-neuro-omission-ghost-signals

## Purpose
Quantifies "Neural Ghosts" — stimulus-specific persistence during physical omission. Tests the Blackboard hypothesis (PFC→V1 Deep paints expectation).

## Input
| Name | Type | Description |
|------|------|-------------|
| omit_activity | ndarray(T,) | Per-unit firing rate during omission (expected-A) |
| stim_template | ndarray(T,) | Clean neural response to actual stimulus A |
| population_vectors | ndarray(units, T) | Multi-unit state across hierarchy |

## Output
| Name | Type | Description |
|------|------|-------------|
| ghost_score | float | Pearson r between omission and stimulus template |
| persistence_ms | int | Duration ghost signal remains significant |

## Example
```python
import numpy as np
ghost = np.corrcoef(omit_A, stim_A)[0, 1]
print(f"""[result] Ghost score: {ghost:.3f}""")
```

## Files
- [contextual_persistence.py](file:///D:/drive/omission/src/analysis/contextual_persistence.py) — Implementation
