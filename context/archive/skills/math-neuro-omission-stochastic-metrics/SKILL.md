---
name: math-neuro-omission-stochastic-metrics
---
# math-neuro-omission-stochastic-metrics

## Purpose
Information-theoretic formalisms: Fano Factor, Mutual Information, KL-Divergence for neural variability and surprise quantification.

## Key Formulas
| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Fano Factor | `σ² / μ` | <1 regular, >1 bursty |
| Mutual Information | `H(X) - H(X\|Y)` | bits of stimulus info |
| KL-Divergence | `Σ P(i) log(P(i)/Q(i))` | distance between distributions |

## Example
```python
import numpy as np
def fano(counts): return np.var(counts) / (np.mean(counts) + 1e-12)
def kl_div(p, q):
    p, q = np.array(p)+1e-12, np.array(q)+1e-12
    return np.sum(p * np.log2(p / q))
print(f"""[result] FF={fano(spike_counts):.3f}, KL={kl_div(p, q):.3f}""")
```

## Files
- [information.py](file:///D:/drive/omission/src/math/information.py) — Shannon metrics
