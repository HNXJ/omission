---
name: analysis-neuro-omission-population-manifolds
---
# analysis-neuro-omission-population-manifolds

## Purpose
Projects neural population activity into low-dimensional manifolds (PCA/GPFA). Measures state-space trajectory divergence between Stimulus and Omission. Absorbs `analysis-population-coding`.

## Input
| Name | Type | Description |
|------|------|-------------|
| spike_matrix | ndarray(trials, units, T) | Smoothed firing rates |
| area_labels | list[str] | For area-specific manifold analysis |
| n_components | int | Dimensionality target (default: 3) |

## Output
| Name | Type | Description |
|------|------|-------------|
| trajectories | ndarray(trials, n_components, T) | Projected coordinates |
| divergence | float | Mahalanobis distance between Omission/Stimulus clusters |
| explained_var | ndarray(n_components,) | Scree values |

## Example
```python
from sklearn.decomposition import PCA
pca = PCA(n_components=3)
projected = pca.fit_transform(X_spikes)
print(f"""[result] Explained: {sum(pca.explained_variance_ratio_):.2%}""")
```

## Files
- [run-manifold-suite-comprehensive.py](file:///D:/drive/omission/codes/scripts/analysis/run-manifold-suite-comprehensive.py) — Orchestrator
