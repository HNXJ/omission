---
name: math-neuro-omission-connectivity-metrics
---
# math-neuro-omission-connectivity-metrics

## Purpose
Formalisms for PPC (bias-free SFC), Spectral Harmony (power envelope correlations), and Granger Causality (directed influence). Absorbs `analysis-neuro-omission-effective-connectivity`.

## Key Formulas
| Metric | Formula | Range |
|--------|---------|-------|
| PPC | `Σ cos(θ_i - θ_j) / C(N,2)` | [-1, 1] |
| Spectral Harmony | Pearson(envelope_A, envelope_B) | [-1, 1] |
| Granger F | `ln(Var_restricted / Var_unrestricted)` | [0, ∞) |
| Directionality Index | `(GC_FF - GC_FB) / (GC_FF + GC_FB)` | [-1, 1] |

## Input
| Name | Type | Description |
|------|------|-------------|
| signal_pairs | tuple(ndarray, ndarray) | LFP-LFP or Spike-LFP pairs |
| phases | ndarray(N_spikes,) | Instantaneous phases via Hilbert |
| maxlag | int | AR model order for Granger |

## Output
| Name | Type | Description |
|------|------|-------------|
| ppc | float | Phase consistency score |
| adjacency | ndarray(11, 11) | Inter-area connectivity matrix |
| gc_spectrum | ndarray(F,) | Frequency-resolved causality |

## Example
```python
import numpy as np
sum_w = np.sum(spikes)
sum_w2 = np.sum(spikes**2)
ppc = ((sum_cos**2 + sum_sin**2) - sum_w2) / (sum_w**2 - sum_w2)
print(f"""[result] PPC = {ppc:.4f}""")
```

## Files
- [connectivity.py](file:///D:/drive/omission/src/math/connectivity.py) — PPC + Granger
