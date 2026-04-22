---
name: analysis-rsa-cka
description: Protocol for comparing representational geometries using Representational Similarity Analysis (RSA) and Centered Kernel Alignment (CKA).
---
# skill: analysis-rsa-cka

## When to Use
Use this skill when quantifying the similarity between neural representations in different modalities or brain areas. It is essential for:
- Comparing Spiking manifolds with LFP representational geometry.
- Measuring "Representational Decay" across the cortical hierarchy (e.g., V1 vs. PFC).
- Validating Model vs. Brain similarity (e.g., RNN hidden states vs. recorded neurons).
- Detecting "Identity Flip" during omission (how much stimulus identity A vs B is preserved).

## What is Input
- **Feature Matrices**: Activity vectors `(items, features)` where items are condition/time pairs and features are neurons or channels.
- **RDMs**: Dissimilarity matrices `(items, items)` representing representational distance.
- **CKA Kernels**: Gram matrices for second-order similarity alignment.

## What is Output
- **CKA Scores**: Scalar values [0, 1] representing the degree of representational alignment.
- **Similarity Heatmaps**: 11x11 inter-area matrices showing the "Representational Map" of the brain.
- **Dendrograms**: Hierarchical clustering of areas based on representational similarity.

## Algorithm / Methodology
1. **RDM Construction**: Computes the dissimilarity (1 - Pearson r) between all pairs of [Condition x Time] items.
2. **Linear CKA**: Uses Centered Kernel Alignment to compare two feature matrices (X and Y). CKA is preferred over RSA because it is invariant to orthogonal transformations and scaling.
3. **Bicubic Smoothing**: Applies `zsmooth='best'` in Plotly heatmaps to generate publication-quality gradients.
4. **Delta-RSA**: Focuses on the *change* in similarity between stimulus and omission windows.
5. **Hierarchical Decay**: Quantifies how similarity decreases as functional distance increases across the hierarchy.

## Placeholder Example
```python
from src.analysis.geometry import compute_cka, build_rdm

# 1. Build Representational Dissimilarity Matrix
rdm = build_rdm(feature_matrix_v1)

# 2. Compare V1 and PFC using CKA
score = compute_cka(X_v1, X_pfc)
print(f"Representational alignment: {score:.3f}")
```

## Relevant Context / Files
- [analysis-population-coding](file:///D:/drive/omission/.gemini/skills/analysis-population-coding/skill.md) — For manifold extraction.
- [src/analysis/geometry.py](file:///D:/drive/omission/src/analysis/geometry.py) — CKA and RDM implementations.
