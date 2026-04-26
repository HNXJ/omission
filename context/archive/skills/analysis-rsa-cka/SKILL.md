---
name: analysis-rsa-cka
---
# analysis-rsa-cka

## Purpose
Compares representational geometries across brain areas using Representational Similarity Analysis (RSA) and Centered Kernel Alignment (CKA). Detects identity preservation and representational decay.

## Input
| Name | Type | Description |
|------|------|-------------|
| X, Y | ndarray(items, features) | Activity matrices from two sources |
| rdm | ndarray(items, items) | Dissimilarity matrix (1 - Pearson r) |

## Output
| Name | Type | Description |
|------|------|-------------|
| cka_score | float | [0, 1] representational alignment |
| similarity_heatmap | ndarray(11, 11) | Inter-area similarity matrix |

## Example
```python
from src.analysis.geometry import compute_cka, build_rdm
rdm = build_rdm(feature_matrix_v1)
score = compute_cka(X_v1, X_pfc)
print(f"""[result] CKA alignment: {score:.3f}""")
```

## Files
- [geometry.py](file:///D:/drive/omission/src/analysis/geometry.py) — CKA/RDM implementations
