# Figure f046: State-Space Trajectories
## Overview
Visualizes the evolution of population activity in a reduced-dimensional space (PCA/t-SNE) across stimulus and omission trials.

## Key Findings
- Neural trajectories for standard trials follow a highly stereotypical path.
- Omission trials trigger a dynamic "error trajectory" that diverges significantly from the baseline after 100ms.
- Trajectory divergence is maximized in higher hierarchical areas (PFC/FEF).

## Methodology
- PCA applied to the [Trials x Time x Units] firing rate tensor.
- Smoothing: 50ms Gaussian window.
- Normalization: Z-score relative to baseline.
