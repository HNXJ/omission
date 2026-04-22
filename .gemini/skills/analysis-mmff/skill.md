---
name: analysis-mmff
description: Mean-Matched Fano Factor (MMFF) computation and plotting suite. Standardizes neural variability analysis across areas and conditions.
---
# skill: analysis-mmff

## When to Use
Use this skill for all neural variability analyses. It is essential for:
- Computing firing-rate-normalized variability (Fano Factor).
- Comparing quenching of variability across standard vs. omission conditions.
- Ranking brain areas by their variability dynamics (Hierarchy analysis).

## What is Input
- **Spike Data**: `.npy` arrays of spike counts or timestamps.
- **Metadata**: NWB file for unit-to-area mapping.
- **Parameters**: Sliding window size (150ms), step size (5ms), and smoothing sigma (5.0).

## What is Output
- **MMFF Traces**: Time-resolved variability values for each area and condition (`checkpoints/area_mmff_traces.json`).
- **Figures**: Interactive Plotly HTML files showing quenching and variability hierarchies.

## Algorithm / Methodology
1. **Unit Mapping**: Correlates spike indices with electrode locations in the NWB file.
2. **Mean-Matching**: Crucial step to decouple variability from firing rate changes. It equalizes the firing rate distributions across all time bins by subsampling units.
3. **Sliding Window**: Calculates variance and mean in overlapping windows.
4. **Smoothing**: Applies a NaN-safe Gaussian filter to the final traces.
5. **Visualization**: Adheres to the Madelane Golden Dark theme with shaded SEM regions.

## Placeholder Example
```python
from src.analysis.mmff_pipeline import compute_mmff, plot_mmff

# 1. Compute
mmff_data = compute_mmff(
    spike_path='spikes.npy',
    nwb_path='session.nwb',
    win_size=150,
    step=5
)

# 2. Plot
fig = plot_mmff(mmff_data, area='V1')
fig.write_html('outputs/v1_mmff.html')
```

## Relevant Context / Files
- [omission_hierarchy_utils.py](file:///D:/drive/omission/codes/functions/omission_hierarchy_utils.py) — Core functions.
- [compute_mean_matched_fano.py](file:///D:/drive/omission/codes/scripts/compute_mean_matched_fano.py) — Orchestrator.
- [analysis-lfp-pipeline](file:///D:/drive/omission/.gemini/skills/analysis-lfp-pipeline/skill.md) — For related spectral standards.
