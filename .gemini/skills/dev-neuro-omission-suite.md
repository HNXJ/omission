---
name: dev-neuro-omission-suite
description: "Unified analysis pipeline for omission dynamics, TFR, variability quenching, and vault visualization."
version: 2.0
---

## ## Context
Standardizes the computational implementation of the sequential visual omission task analysis across 13 sessions.

## ## Rules
- **TFR Standard**: 100ms Hanning window, 98% overlap. Smooth with 20ms Gaussian width.
- **Relative Power**: Metric: $10 \times \log_{10}(P_{time} / P_{baseline})$. Baseline: Average of delays surrounding the omission window (~1531ms window).
- **Variability**: Use Mean-Matched Fano Factor (MMFF) for spikes and Mean-Matched Variation (MMV) for continuous LFP.
- **Hierarchical Scaling**: Always scale analyses to all 11 brain areas (V1 to PFC). For cross-area metrics (RSA, Granger, CCG), generate 11x11 matrices.
- **Eye Source Standard**: Always source oculomotor data from raw `.mat` BHV files (`bhvUni.AnalogData.Eye`) for maximum DVA precision.
- **Vault Organization**: Store all technical reports in `figures/part01/`. Save as HTML and SVG.
- **Safety Protocol**: If a plot contains all `NaN` or `0` values, DO NOT SAVE. Log an investigation task in `plans/`.
- **Aesthetic**: Use Madelane Golden Dark theme (#CFB87C, #000000, #8F00FF). Shaded SEM at 0.2 opacity.
- **Viewer**: Standard dashboard at `localhost:8181`. Assets vault at `figures/part01/`.

## ## Examples
```python
# TFR Overlap Calculation
nperseg = int(W_MS * FS / 1000)
noverlap = int(0.98 * nperseg)
# Relative Power Change
rel_db = 10 * np.log10(avg_trial_tfr / (baseline_power + 1e-12))
```

# # Keywords:
# TFR, Spectrogram, MMFF, MMV, Quenching, Omission Dynamics, Analysis Viewer, Golden Dark, SEM, Spectral Power.
