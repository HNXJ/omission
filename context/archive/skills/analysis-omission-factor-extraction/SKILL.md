---
name: analysis-omission-factor-extraction
---
# analysis-omission-factor-extraction

## Purpose
Extracts 48 neural features per neuron (12 intervals × 4 metrics: mean_fr, std_isi, mean_var, std_var) for population-level classification and R-based factor analysis. Absorbs `omission-factors`.

## Input
| Name | Type | Description |
|------|------|-------------|
| nwb_dir | str | For unit-to-area mapping |
| array_dir | str | Binned spike matrices in `data/arrays/` |
| layer_csv | str | `checkpoints/real_omission_units_layered_v3.csv` |

## Output
| Name | Type | Description |
|------|------|-------------|
| feature_csv | str | `checkpoints/omission_neurons_r_factors.csv` — 48 columns + metadata |

## Metrics
| Metric | Formula | Meaning |
|--------|---------|---------|
| mean_fr | spikes/sec | Average firing rate |
| std_isi | σ(ISI) | Regularity (lower = more regular) |
| mean_var | E[Var(trials)] | Across-trial variability |
| std_var | σ(Var(trials)) | Volatility of variance |

## Example
```python
from src.extract.omission_factors import extract_factors
df = extract_factors(nwb_dir="data/nwb/", array_dir="data/arrays/")
print(f"""[result] {len(df)} units × {len(df.columns)} features""")
print(df[['session', 'area', 'RRXR_omit_mean_fr']].head())
```

## Files
- [extract_omission_factors.py](file:///D:/drive/omission/src/extract/extract_omission_factors.py) — Core logic