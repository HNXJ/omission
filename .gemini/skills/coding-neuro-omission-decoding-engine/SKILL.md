---
name: coding-neuro-omission-decoding-engine
description: High-performance machine learning suite for quantifying stimulus and omission information fidelity using SVM and PEV.
---
# skill: coding-neuro-omission-decoding-engine

## When to Use
Use this skill when implementing population-level classification or variance analysis. It is the primary tool for:
- Decoding stimulus identity (A vs. B) during the presentation window.
- Testing for "Information Persistence" during the omission window.
- Calculating Percent Explained Variance (PEV) to map where information is localized in the brain.
- Performing Temporal Generalization (train on time t1, test on t2) to detect stable vs. dynamic representations.

## What is Input
- **Feature Matrices**: `(trials, units)` or `(trials, units, time_bins)`.
- **Label Vectors**: Categorical target variables (e.g., 0 for StimA, 1 for StimB).
- **Time Windows**: Specific bins (e.g., 50ms sliding windows) for dynamic decoding.

## What is Output
- **Decoding Accuracy**: Time-resolved classification performance (chance-level = 50% for binary).
- **Generalization Matrices**: 2D heatmaps of (Train Time x Test Time) accuracy.
- **PEV Maps**: Anatomical or depth-resolved fidelity of task information.

## Algorithm / Methodology
1. **Linear SVM**: Uses `sklearn.svm.LinearSVC` for robust, high-dimensional classification.
2. **Stratified Cross-Validation**: Implements 10-fold CV to ensure that results generalize across trial subsets.
3. **PEV Calculation**: Computes `(SS_between - df * MS_error) / (SS_total + MS_error)` to provide a bias-corrected measure of explained variance.
4. **Permutation Testing**: Runs 1000 shuffles of label vectors to establish a statistical significance baseline (p < 0.05).
5. **Temporal Generalization**: Trains a classifier at each time point and tests it on all other time points to identify "Dynamic" vs. "Static" coding regimes.

## Placeholder Example
```python
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score

# 1. Initialize the linear decoding engine
clf = LinearSVC(max_iter=5000, dual=False)

# 2. Run 10-fold cross-validation on stimulus identity
scores = cross_val_score(clf, X_units, y_labels, cv=10)
print(f"Identity Decoding Accuracy: {scores.mean():.2%}")
```

## Relevant Context / Files
- [analysis-population-coding](file:///D:/drive/omission/.gemini/skills/analysis-population-coding/skill.md) — For manifold-level features.
- [src/analysis/decoding.py](file:///D:/drive/omission/src/analysis/decoding.py) — The core implementation of the decoding engine.
