---
name: analysis-neuro-omission-effective-connectivity
description: "Omission analysis skill focusing on analysis neuro omission effective connectivity."
---

# Effective Connectivity and Granger Causality

While functional connectivity measures correlation, effective connectivity aims to determine the directed influence (causality) of one area over another.

Granger Causality (GC):
A signal X is said to Granger-cause Y if the past values of X help predict the future values of Y better than the past values of Y alone. We use bivariate and multivariate autoregressive (MVAR) models to estimate directed flow.

Key Findings:
In our V1-PFC hierarchy, we observe a reversal of information flow during omissions.
- Stimulus Periods: V1 -> PFC (Feedforward, Gamma-dominated).
- Omission Periods: PFC -> V1 (Feedback, Beta/Alpha-dominated).
This directed influence is the smoking gun for top-down prediction error propagation.

Technical Implementation:
```python
from statsmodels.tsa.stattools import grangercausalitytests
def check_granger(data_matrix, maxlag=20):
    # data_matrix: (Time, 2)
    results = grangercausalitytests(data_matrix, maxlag=maxlag, verbose=False)
    # Extract p-values or F-statistics
    return results
```

References:
1. Seth, A. K., et al. (2015). Granger causality analysis in neuroscience and neuroimaging. Journal of Neuroscience.
2. Friston, K. J. (2011). Functional and effective connectivity: a review. Brain Connectivity.
