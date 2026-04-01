---
name: analysis-neuro-omission-field-dynamics
description: "Analysis of regional field dynamics, connectivity, and spectral coordination."
version: 1.0
---

## ## Context
Standardizes the quantification of LFP-based metrics for the omission hierarchy.

## ## Rules
- **Connectivity**: Default to Spectral Granger Causality (V1 <-> PFC). Order 15 for AR model.
- **Phase**: Compute Phase-Lag Index (PLI) and Coherence for cross-area coordination.
- **PPC**: Calculate Pairwise Phase Consistency (PPC) to measure spike-field coupling.
- **Spectrograms**: Use Hanning window, 98% overlap, 1-150Hz range. Always use ms for x-axis.
- **Granger**: Channel 0 = V1, Channel 1 = PFC for standard pairwise checks.

## ## Examples
```python
# Spectral Granger Logic
tseries = ts.TimeSeries(combined, sampling_rate=FS)
g_analyzer = na.GrangerAnalyzer(tseries, order=15)
# Phase Lag
f, Cxy, phase = compute_phase_lag(sig1, sig2, fs)
```

# # Keywords:
# LFP, Granger Causality, Connectivity, Phase-Lag, Coherence, PPC, Spectrogram, Field Dynamics, Cortical Hierarchy.
