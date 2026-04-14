---
name: math-neuro-omission-connectivity-metrics
description: "Omission analysis skill focusing on math neuro omission connectivity metrics."
---

# Connectivity Metrics & Formalisms

Quantitative definitions for connectivity analysis allow for objective assessment of network interactions.

1. Cross-Spectral Density (CSD):
The Fourier transform of the cross-correlation function. It describes the covariance between two signals in the frequency domain.

2. Coherence (C):
C_xy(f) = |S_xy(f)|^2 / (S_xx(f) * S_yy(f)). A normalized measure of linear relationship between signals x and y at frequency f.

3. Granger Causality (F):
F = ln(Var_restricted / Var_unrestricted). Quantifies the reduction in prediction error of signal Y when signal X is included in the autoregressive model.

Adjacency Matrices:
We represent the 11-area network as an adjacency matrix A where A_ij represents the strength of connection (Coherence or GC) from area i to area j.

Formulae:
- Phase Difference: theta = angle(S_xy(f))
- Coherency: s_xy(f) = S_xy(f) / sqrt(S_xx(f) * S_yy(f))

Implementation:
```python
# Conceptual implementation
def bivariate_granger_concept(x, y, p=10):
    # Simplified AR model fit comparison logic
    # In practice, use statsmodels.tsa.stattools.grangercausalitytests
    pass
```

References:
1. Nolte, G., et al. (2004). Identifying true brain interaction from EEG data using the imaginary part of coherency. Clinical Neurophysiology.
2. Barrett, A. B., & Seth, A. K. (2011). Practical guidelines for Granger causality analysis of multivariate time series. Journal of Neuroscience Methods.
