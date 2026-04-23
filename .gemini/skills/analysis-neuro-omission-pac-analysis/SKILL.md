---
name: analysis-neuro-omission-pac-analysis
---
# analysis-neuro-omission-pac-analysis

## Purpose
Computes Phase-Amplitude Coupling (PAC) via the Tort Modulation Index (MI). Quantifies how low-frequency phase (Theta) modulates high-frequency amplitude (Gamma).

## Input
| Name | Type | Description |
|------|------|-------------|
| lfp_trace | ndarray(T,) | Raw or broadband LFP |
| f_phase | tuple | Low-freq band (e.g. `(4, 8)` Hz) |
| f_amp | tuple | High-freq band (e.g. `(40, 80)` Hz) |
| n_bins | int | Phase bins (default: 18) |

## Output
| Name | Type | Description |
|------|------|-------------|
| mi_value | float | Modulation Index (KL-divergence from uniform) |
| comodulogram | ndarray(F_phase, F_amp) | MI heatmap over frequency pairs |

## Example
```python
from src.analysis.pac import calculate_modulation_index
mi = calculate_modulation_index(lfp_trace, f_phase=(4,8), f_amp=(40,80), n_bins=18)
print(f"""[result] MI = {mi:.6f}""")
```

## Files
- [pac.py](file:///D:/drive/omission/src/analysis/pac.py) — Core implementation
