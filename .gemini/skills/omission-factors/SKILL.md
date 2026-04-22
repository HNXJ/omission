---
name: omission-factors
description: Framework for characterizing neuron-specific dynamics via 48-factor feature extraction (Rate, Regularity, Variability, Volatility).
---
# skill: omission-factors

## When to Use
Use this skill when performing dimensionality reduction or functional clustering of neural populations. It is mandatory for:
- Constructing the "48-Factor Matrix" per neuron (12 intervals $\times$ 4 metrics).
- Characterizing firing regularity via ISI standard deviation (`std_isi`).
- Quantifying across-trial variability (`mean_var`) and volatility (`std_var`).
- Preparing data for PCA/UMAP embedding of population state trajectories.

## What is Input
- **Spike Tensors**: High-resolution binned counts across the full trial duration.
- **Interval Definitions**: 12 specific windows (Fixation, Pre-Omission, Omission, Post-Omission).
- **Laminar Labels**: Mandatory metadata (Session, Area, Channel, Layer).

## What is Output
- **Feature Matrix**: `omission_neurons_r_factors.csv` containing the 48 factors per unit.
- **Visualizations**: Dimensionality reduction plots (PCA/UMAP) showing clustering by area or response type.

## Algorithm / Methodology
1. **Metric Definition**:
   - `mean_fr`: Mean firing rate (Hz).
   - `std_isi`: Regularity metric (Lower = more regular).
   - `mean_var`: Across-trial variance (Variability).
   - `std_var`: Volatility of variance (State stability).
2. **Interval Mapping**: 12 windows selected to capture the transition from expectation to surprise.
3. **Filtering**: Restricts to "Stable-Plus" units (FR > 1Hz, SNR > 0.8).
4. **Context Enrichment**: Attaches session-level metadata and laminar positions (Deep vs. Superficial).

## Placeholder Example
```python
import pandas as pd
from sklearn.decomposition import PCA

# 1. Load the 48-Factor Matrix
df = pd.read_csv('checkpoints/omission_neurons_r_factors.csv')
features = df.filter(regex='_mean_|_std_')

# 2. Run Dimensionality Reduction
pca_results = PCA(n_components=2).fit_transform(features)
# Scatter plot of PC1 vs PC2 colored by 'area'
```

## Relevant Context / Files
- [nwb-analysis](file:///D:/drive/omission/.gemini/skills/nwb-analysis/skill.md) — For the raw variability calculation.
- [src/analysis/feature_extraction.py](file:///D:/drive/omission/src/analysis/feature_extraction.py) — The logic generating the factors.
