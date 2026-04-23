---
name: coding-neuro-omission-signal-conditioning
---
# coding-neuro-omission-signal-conditioning

## Purpose
DSP suite: spike→PSTH smoothing, Z-scoring, band-pass filtering (Butterworth), Hilbert phase/amplitude extraction, MUAe computation.

## Input
| Name | Type | Description |
|------|------|-------------|
| raw_tensor | ndarray(trials, ch, T) | Absolute units (µV or binary spikes) |
| fs | float | Sampling rate (1000 Hz or 30 kHz) |
| baseline_win | tuple | Window for normalization (e.g. -500 to 0 ms) |

## Output
| Name | Type | Description |
|------|------|-------------|
| psth | ndarray | Gaussian-smoothed firing rates (Hz) |
| z_signal | ndarray | Z-scored relative to baseline |
| analytic | ndarray(complex) | Hilbert transform (phase + envelope) |

## Key Parameters
- Gaussian σ: 20ms (spike smoothing)
- Butterworth: zero-phase via `scipy.signal.filtfilt`
- MUAe: rectify 1-3kHz band → 200Hz LPF

## Example
```python
from scipy.ndimage import gaussian_filter1d
psth = gaussian_filter1d(spikes.astype(float), sigma=20, axis=2) * 1000
baseline_mu = psth[:,:,:500].mean(axis=(0,2), keepdims=True)
baseline_sd = psth[:,:,:500].std(axis=(0,2), keepdims=True)
z_psth = (psth - baseline_mu) / (baseline_sd + 1e-6)
print(f"""[result] Z-PSTH shape: {z_psth.shape}""")
```

## Files
- [signal_processing.py](file:///D:/drive/omission/src/analysis/signal_processing.py) — Implementation
