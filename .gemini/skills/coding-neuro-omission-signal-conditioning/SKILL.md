---
name: coding-neuro-omission-signal-conditioning
description: Advanced DSP suite for smoothing, normalizing, and filtering neural time-series data (Spikes, LFP, MUA).
---
# skill: coding-neuro-omission-signal-conditioning

## When to Use
Use this skill for all "Level 1" preprocessing tasks that follow data loading. It is critical for:
- Converting discrete spikes into continuous Peristimulus Time Histograms (PSTH).
- Z-scoring firing rates against a pre-stimulus baseline to handle inter-unit variability.
- Band-pass filtering LFP into canonical oscillations (Alpha, Beta, Gamma).
- Removing 60Hz line noise using Notch filters.
- Extracting Multi-Unit Activity envelope (MUAe) via rectification and low-pass filtering.

## What is Input
- **Raw Tensors**: `(trials, channels, samples)` in absolute units (µV or binary spikes).
- **Metadata**: Sampling rate (usually 1000Hz or 30kHz).
- **Window Definitions**: Baseline windows (e.g., -500ms to 0ms) for normalization.

## What is Output
- **Smoothed PSTHs**: Continuous firing rate estimates in Hz.
- **Normalized Signals**: Unitless Z-scored or min-max scaled data.
- **Analytic Signals**: Complex-valued time-series (from Hilbert transform) for phase analysis.

## Algorithm / Methodology
1. **Gaussian Smoothing**: Convolves spike trains with a 1D Gaussian kernel (`sigma=20ms` default).
2. **Baseline Z-Scoring**: Calculates `(x - mu_baseline) / sigma_baseline` to stabilize variance across units.
3. **Butterworth Filters**: Implements zero-phase (causal-corrected) filtering using `scipy.signal.filtfilt`.
4. **Hilbert Transform**: Extracts the instantaneous phase and amplitude envelope for Phase-Amplitude Coupling (PAC).
5. **MUAe Extraction**: Rectifies the 1kHz-3kHz band and applies a 200Hz low-pass filter to estimate local population spikes.

## Placeholder Example
```python
from scipy.ndimage import gaussian_filter1d

# 1. Smooth the spikes (trials, units, time)
psth = gaussian_filter1d(spike_array.astype(float), sigma=20, axis=2) * 1000

# 2. Z-score relative to the first 500ms
baseline_mu = psth[:, :, :500].mean(axis=(0, 2), keepdims=True)
baseline_sd = psth[:, :, :500].std(axis=(0, 2), keepdims=True)
z_psth = (psth - baseline_mu) / (baseline_sd + 1e-6)
```

## Relevant Context / Files
- [coding-neuro-omission-nwb-pipeline](file:///D:/drive/omission/.gemini/skills/coding-neuro-omission-nwb-pipeline/skill.md) — For initial data access.
- [src/analysis/signal_processing.py](file:///D:/drive/omission/src/analysis/signal_processing.py) — The main implementation library.
