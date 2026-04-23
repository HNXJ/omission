---
name: analysis-neuro-omission-functional-connectivity
---
# analysis-neuro-omission-functional-connectivity

## Purpose
Quantifies inter-area synchronization via Power Envelope Correlations ("Spectral Harmony") and bias-free Pairwise Phase Consistency (PPC).

## Input
| Name | Type | Description |
|------|------|-------------|
| power_envelopes | ndarray(11, T) | Time-resolved band power per area |
| spike_phases | ndarray(N_spikes,) | LFP phases at spike times |
| regional_mask | dict | Grouping of electrodes into 11 areas |

## Output
| Name | Type | Description |
|------|------|-------------|
| harmony_matrix | ndarray(11, 11) | Pearson correlation of power envelopes |
| ppc_spectrum | ndarray(F,) | Phase consistency across 1-100 Hz |

## Key Formula
- **PPC**: `(Σ cos(θ_i - θ_j)) / C(N,2)` — bias-free alternative to PLV

## Example
```python
import numpy as np
envelopes = np.random.rand(11, 1000)
harmony = np.corrcoef(envelopes)
assert np.allclose(np.diag(harmony), 1.0)
print(f"""[result] Harmony matrix shape: {harmony.shape}""")
```

## Files
- [connectivity.py](file:///D:/drive/omission/src/analysis/connectivity.py) — Core implementation
