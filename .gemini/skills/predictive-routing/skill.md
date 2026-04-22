---
name: predictive-routing
description: Advanced LFP analysis engine (CSD, TFR), oculomotor controls, and statistical validation (Permutation, GLM) for the Predictive Routing paradigm.
---
# skill: predictive-routing

## When to Use
Use this skill for high-fidelity LFP analysis and statistical validation of laminar motifs. It is mandatory for:
- Identifying Layer 4 sinks via Current Source Density (CSD) analysis.
- Performing parallel multi-band spectral decomposition using the JAX-vectorized Morlet engine.
- Purging microsaccade-contaminated trials (>30 deg/s) using the Engbert & Kliegl protocol.
- Executing cluster-based permutation tests on Time-Frequency Representations (TFRs).
- Dissociating Feedforward (Gamma) from Feedback (Beta) signals via ERP subtraction.

## What is Input
- **LFP Signals**: Raw or downsampled local field potentials from linear probes.
- **Eye-Tracking Data**: Raw $(x, y)$ gaze positions for microsaccade detection.
- **Event Codes**: Timing markers for task-logic state machines.

## What is Output
- **CSD Profiles**: Spatial Laplacian maps for layer assignment.
- **TFR Tensors**: Time-frequency-power arrays organized by condition and area.
- **Statistical Clusters**: Significant time-frequency regions (p < 0.05) corrected for multiple comparisons.

## Algorithm / Methodology
1. **Layer Assignment**: CSD sink identification on the average Visual Evoked Potential (VEP).
2. **Spectral Engine**: JAX-vectorized Morlet wavelets with parallel multi-band support.
3. **Induced vs. Evoked**: ERP subtraction to isolate non-phase-locked oscillations.
4. **Clean Trials**: Microsaccade rejection using velocity-space thresholding.
5. **Connectivity**: Weighted Phase Lag Index (wPLI) to assess inter-areal coordination without volume conduction bias.

## Placeholder Example
```python
# 1. Identify Layer 4 Sink
# csd_profile is a 2D map (Channels x Time)
csd_profile = predictive_routing.compute_1d_csd(average_vep)

# 2. Run Parallel TFR
# Induced power only (ERP subtracted)
tfr_power = predictive_routing.compute_tfr_jax(lfp_tensors, subtract_erp=True)
```

## Relevant Context / Files
- [lfp-core](file:///D:/drive/omission/.gemini/skills/lfp-core/skill.md) — For fundamental LFP processing.
- [src/spectral/wavelet_engine.py](file:///D:/drive/omission/src/spectral/wavelet_engine.py) — The JAX implementation of the Morlet transform.
