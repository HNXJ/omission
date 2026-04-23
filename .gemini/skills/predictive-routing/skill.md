---
name: predictive-routing
---
# predictive-routing

## Purpose
Advanced LFP engine: CSD for layer sinks, JAX-vectorized Morlet TFR, microsaccade rejection, cluster permutation tests, wPLI connectivity.

## Input
| Name | Type | Description |
|------|------|-------------|
| lfp_signals | ndarray(C, T) | Raw LFP from linear probes |
| eye_data | ndarray(2, T) | Gaze XY for microsaccade filtering |
| event_codes | list[int] | Task state machine markers |

## Output
| Name | Type | Description |
|------|------|-------------|
| csd_profile | ndarray(C, T) | Current Source Density map |
| tfr_tensor | ndarray(F, T) | Time-frequency power (induced) |
| stat_clusters | list[dict] | Significant TF regions (p<0.05 corrected) |

## Methods
- CSD: spatial Laplacian on average VEP
- TFR: Morlet wavelets, ERP subtracted for induced power
- Clean trials: reject velocity > 30 deg/s
- Connectivity: wPLI (volume-conduction resistant)

## Example
```python
csd = predictive_routing.compute_1d_csd(average_vep)
tfr = predictive_routing.compute_tfr_jax(lfp, subtract_erp=True)
print(f"""[result] TFR shape: {tfr.shape}""")
```

## Files
- [wavelet_engine.py](file:///D:/drive/omission/src/spectral/wavelet_engine.py) — JAX Morlet
