---
name: coding-neuro-omission-decoding-engine
---
# coding-neuro-omission-decoding-engine

## Purpose
SVM/PEV-based decoding of stimulus identity and omission state. Temporal generalization matrices and permutation testing. Absorbs `science-neuro-omission-identity-coding`.

## Input
| Name | Type | Description |
|------|------|-------------|
| X | ndarray(trials, units) or (trials, units, T) | Feature matrices |
| y | ndarray(trials,) | Categorical labels (0=StimA, 1=StimB) |
| cv_folds | int | Cross-validation (default: 10) |
| n_permutations | int | Shuffle count for significance (default: 1000) |

## Output
| Name | Type | Description |
|------|------|-------------|
| accuracy_trace | ndarray(T,) | Time-resolved classification performance |
| gen_matrix | ndarray(T, T) | Train-time × Test-time accuracy heatmap |
| pev_map | ndarray(units, T) | Percent Explained Variance per unit/time |
| p_threshold | float | Permutation-derived significance cutoff |

## Key Formulas
- **PEV**: `(SS_between - df * MS_error) / (SS_total + MS_error)`
- **Chance**: 50% (binary), 33% (ternary A/B/R)

## Example
```python
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score
clf = LinearSVC(max_iter=5000, dual=False)
scores = cross_val_score(clf, X_units, y_labels, cv=10)
print(f"""[result] Decoding accuracy: {scores.mean():.2%}""")
```

## Files
- [decoding.py](file:///D:/drive/omission/src/analysis/decoding.py) — Core engine
