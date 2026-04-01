---
name: analysis-neuro-omission-population-coding
description: "High-dimensional analysis of spiking population dynamics, decoding, and manifolds."
version: 1.0
---

## ## Context
Quantifies how the neural population encodes identity (A vs B) and omission detection across the cortical hierarchy.

## ## Rules
- **Manifolds**: Use PCA/t-SNE to visualize population trajectories. Standard: 3-5 principal components.
- **Decoding**: Use SVM (Linear Kernel) for binary classification (Omit vs Delay, A vs B).
- **Metric**: Decoding accuracy (%) across a sliding 50ms window.
- **Cross-Validation**: 5-fold CV with trial-balanced splits.
- **Factor Matrix**: Extract 48 factors per neuron for population dynamics analysis (Omission Factors).
- **Latencies**: Identify the earliest time-to-peak for surprise response (Avg Peak Lag: ~38ms for PFC).

## ## Examples
```python
# PCA Trajectory
pca = PCA(n_components=3).fit_transform(trial_matrix)
# SVM Decoding
clf = svm.SVC(kernel='linear').fit(X_train, y_train)
```

# # Keywords:
# Spiking, PCA, SVM Decoding, Population Manifolds, Omission Factors, Latency Analysis, Surprise Propagation.
