---
name: analysis-neuro-omission-unit-classification
---
# analysis-neuro-omission-unit-classification

## Purpose
Categorizes neurons into functional types (S+, O+, S-, O-) based on epoch-specific firing rate ratios. Implements Top-10 indexing for high-fidelity population analysis.

## Input
| Name | Type | Description |
|------|------|-------------|
| spike_matrix | ndarray(trials, units, T) | Binned spike counts |
| epochs | dict | `{fx: (-500,0), p1: (0,531), d1: (531,1031), p2: (1031,1562)}` |

## Output
| Name | Type | Description |
|------|------|-------------|
| unit_labels | dict[str, str] | Unit ID → functional category (S+/O+/S-/O-) |
| top10_indices | dict[str, list] | `{area: {S+: [...], O+: [...]}}` |

## Key Formulas
- **S+ Score**: `Mean(p1) / (Mean(fx) + ε)` — stimulus responsiveness
- **O+ Score**: `Mean(p2) / (Mean(d1) + ε)` — omission responsiveness
- Classification: S+ if Score_S > threshold AND Score_S > Score_O, vice versa

## Example
```python
from src.analysis.classification import get_top_units
top_o_pfc = get_top_units(spk_matrix, area='PFC', type='O+', top_n=10)
print(f"""[result] Top 10 PFC O+ indices: {top_o_pfc}""")
```

## Files
- [classification.py](file:///D:/drive/omission/src/analysis/classification.py) — Core logic
