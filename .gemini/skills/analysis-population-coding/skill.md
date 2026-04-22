---
name: analysis-population-coding
description: Advanced methods for high-dimensional spiking dynamics (manifolds, SVM decoding) and oculomotor proxies (DVA, pupil, micro-saccades).
---
# skill: analysis-population-coding

## When to Use
Use this skill for characterizing the emergent properties of neural populations. It is the gold standard for:
- Mapping the dimensionality of neural space using PCA/t-SNE/UMAP.
- Decoding stimulus identity (A vs. B) or condition (Omission vs. Delay) using SVMs.
- Correlating neural "surprise" with behavioral proxies like pupil dilation or eye jitter.
- Comparing population trajectories across different brain regions to establish the predictive hierarchy.

## What is Input
- **Spike Matrices**: Binned spike counts `(trials, units, time)` from `data/arrays/`.
- **Eye Data**: Raw DVA coordinates from BHV2.mat files.
- **Labels**: Condition vectors (e.g., RXRR, RRXR) and stimulus identities.

## What is Output
- **Decoding Timecourses**: Sliding-window accuracy (%) with 95% CI.
- **Manifold Plots**: 2D/3D projections of the first 3-5 Principal Components.
- **Hierarchy Rankings**: Surprise latencies quantified by trajectory divergence.
- **Behavioral Metrics**: Normalized pupil diameter and eye-fixation variance.

## Algorithm / Methodology
1. **Dimensionality Reduction**: Projects firing rate vectors onto orthogonal axes (PCA) to visualize low-rank dynamics.
2. **SVM Classification**: Uses 5-fold cross-validation with trial-balanced splits to decode conditions in 50ms sliding windows.
3. **Surprise Latency**: Quantifies the first time-point where Omission trajectories diverge significantly (>2SD) from Baseline.
4. **Oculomotor QC**: Cleans eye data using velocity-thresholding (>30 deg/s) to isolate fixations and micro-saccades.
5. **Phase-Consistency**: Implements Pairwise Phase Consistency (PPC) to link single-unit spikes to LFP oscillations (e.g., Gamma vs. Beta).

## Placeholder Example
```python
from sklearn.decomposition import PCA
from sklearn.svm import SVC

# 1. Project to 3D manifold
pca = PCA(n_components=3).fit_transform(X_spikes)
print(f"Explained variance: {pca.explained_variance_ratio_}")

# 2. Decode Omission vs. Delay
clf = SVC(kernel='linear').fit(X_train, y_train)
acc = clf.score(X_test, y_test)
```

## Relevant Context / Files
- [analysis-rsa-cka](file:///D:/drive/omission/.gemini/skills/analysis-rsa-cka/skill.md) — For cross-modal similarity analysis.
- [src/analysis/population.py](file:///D:/drive/omission/src/analysis/population.py) — Core manifold and decoding logic.
