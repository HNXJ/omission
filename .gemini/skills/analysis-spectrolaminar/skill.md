---
name: analysis-spectrolaminar
---
# analysis-spectrolaminar

## Purpose
Spectrolaminar profiling: computes depth-resolved Alpha/Beta vs Gamma power from linear-probe LFP and identifies the L4 crossover channel for laminar assignment.

## Input
| Name | Type | Description |
|------|------|-------------|
| lfp_data | ndarray(C, T) | Raw LFP (n_channels × n_timepoints) |
| fs | float | Sampling frequency (default: 1000 Hz) |
| bands | implicit | Alpha/Beta: 8-30 Hz, Gamma: 35-80 Hz |

## Output
| Name | Type | Description |
|------|------|-------------|
| alpha_beta_profile | ndarray(C,) | Normalized low-freq power per channel |
| gamma_profile | ndarray(C,) | Normalized high-freq power per channel |
| l4_channel | int | Channel index where Gamma > Alpha/Beta (crossover) |

## Example
```python
from codes.functions.vflip2_mapping import compute_spectrolaminar_profiles, find_crossover
profiles = compute_spectrolaminar_profiles(lfp_data, fs=1000.0)
l4 = find_crossover(profiles)
print(f"""[result] L4 crossover at channel {l4}""")
```

## Files
- [vflip2_mapping.py](file:///D:/drive/omission/codes/functions/vflip2_mapping.py) — Core
