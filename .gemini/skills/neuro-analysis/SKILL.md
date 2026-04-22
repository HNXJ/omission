---
name: neuro-analysis
description: Suite for population-level neural analysis, including response classification (S+/O+), decoding, and publication-grade visualization.
---
# skill: neuro-analysis

## When to Use
Use this skill for high-level population dynamics and single-unit auditing. It is mandatory for:
- Classifying neurons into functional types: Stimulus-Responsive (S+, S-), Omission-Responsive (O+, O-), and Prediction-Error units.
- Generating publication-grade "Primate Suite" visualizations (aligned Rasters + Traces).
- Implementing population decoders (SVM/LDA) to track stimulus identity in Deep vs. Superficial layers.
- Mapping NWB global unit indices to probe-local indices for accurate depth estimation.

## What is Input
- **Spike Tensors**: Binned firing rates or binary spike trains categorized by condition.
- **Area Labels**: Definitive mapping (e.g., DP -> V4, V3 -> V3d/V3a).
- **Control Params**: Classification windows (stimulus: 50-150ms; omission: 50-300ms).

## What is Output
- **Classification Reports**: Counts and percentages of S+ vs. O+ units across the hierarchy.
- **Interactive Figures**: HTML-based raster-trace suites with Gaussian-convolved PSTHs.
- **Decoding Accuracies**: Time-resolved performance curves showing information fidelity.

## Algorithm / Methodology
1. **Response Classification**: Uses t-tests comparing firing rates in baseline vs. post-event windows.
2. **Primate Suite Protocol**: Generates 6 panels per neuron (3 Rasters, 3 Traces) with `sigma=50ms` smoothing.
3. **Probe Partitioning**: Implements the 128-channel rule to split combined probes (e.g., "V1/V2") into distinct area segments.
4. **Decoding Protocol**: Employs leave-one-out cross-validation to assess stimulus discriminability.
5. **Stable-Plus Filter**: Restricts analysis to units with FR > 1Hz and SNR > 0.8 for maximum scientific validity.

## Placeholder Example
```python
# 1. Run Response Classification
# Identifies neurons that fire during stimulus omissions
python neuro-analysis/scripts/classify_omission_response.py --data_dir data/

# 2. Generate Standard Visual QA Suite
python neuro-analysis/scripts/plot_raster_trace_suite.py --unit_id 42
```

## Relevant Context / Files
- [design-neuro-omission-branding-theme](file:///D:/drive/omission/.gemini/skills/design-neuro-omission-branding-theme/skill.md) — For aesthetic consistency.
- [neuro-analysis/references/TASK_DETAILS.md](file:///D:/drive/omission/neuro-analysis/references/TASK_DETAILS.md) — Definitive stimulus timings and task rules.
