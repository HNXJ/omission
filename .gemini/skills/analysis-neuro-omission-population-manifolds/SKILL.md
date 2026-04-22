---
name: analysis-neuro-omission-population-manifolds
description: Projects neural population activity into low-dimensional manifolds (PCA/GPFA). Analyzes state-space trajectories during stimulus and omission epochs.
---
# skill: analysis-neuro-omission-population-manifolds

## When to Use
Use this skill to visualize and quantify population-level neural dynamics. It is essential for:
- Identifying distinct neural "attractors" for Omission vs. Stimulus states.
- Measuring the divergence of trajectories in low-dimensional space.
- Quantifying the dimensionality (complexity) of the neural response across areas.

## What is Input
- **Spike Matrix**: `(n_trials, n_units, n_time_bins)` smoothed firing rates.
- **Area Labels**: To perform area-specific manifold analysis.
- **Dimensionality Parameters**: Number of components (e.g., top 3 PCs).

## What is Output
- **Trajectories**: 3D coordinates for each trial/condition in the manifold space.
- **Divergence Scores**: Mahalanobis distance between Omission and Stimulus clusters.
- **Explained Variance**: Scree plots showing the principal components' importance.

## Algorithm / Methodology
1. **Preprocessing**: Gaussian smoothing of trial-aligned spike trains and Z-scoring across time/units.
2. **Dimensionality Reduction**: Applies Principal Component Analysis (PCA) or Gaussian Process Factor Analysis (GPFA) to the population matrix.
3. **Projection**: Maps high-dimensional unit activity onto the top latent factors.
4. **Trajectory Analysis**: Calculates the Euclidean or Mahalanobis distance between the "Standard path" and "Omission path" in the manifold.

## Placeholder Example
```python
from src.analysis.manifolds import compute_pca_projection

# 1. Prepare smoothed population data
pop_data = load_population_spikes(session_id, area='PFC')

# 2. Project to 3D
trajectories, pca_model = compute_pca_projection(pop_data, n_components=3)

# 3. Print explained variance
print(f"Top 3 PCs explain {sum(pca_model.explained_variance_ratio_):.2%} of variance.")
```

## Relevant Context / Files
- [run-manifold-suite-comprehensive.py](file:///D:/drive/omission/codes/scripts/analysis/run-manifold-suite-comprehensive.py) — Core orchestrator.
- [analysis-neuro-omission-unit-classification](file:///D:/drive/omission/.gemini/skills/analysis-neuro-omission-unit-classification/skill.md) — For selecting specific unit types for the manifold.
