---
name: math-neuro-omission-stochastic-metrics
description: "Omission analysis skill focusing on math neuro omission stochastic metrics."
---

# Stochastic Metrics for Neural Analysis

Stochastic metrics quantify the variability and information content of neural signals.

1. Fano Factor (FF):
FF = Var(counts) / Mean(counts). For a Poisson process, FF = 1. FF < 1 indicates a sub-Poisson (regular) process, and FF > 1 indicates a super-Poisson (bursty) process.

2. Mutual Information (MI):
MI(X; Y) = H(X) - H(X|Y). It measures how much uncertainty about variable X is reduced by knowing variable Y. In our task, X is stimulus identity and Y is neural response.

3. Information Gain (KL-Divergence):
D_KL(P||Q) = sum P(i) log(P(i)/Q(i)). Used to measure the update from a prior distribution (Q) to a posterior (P) after a surprise.

Formal Definitions:
- Variance: sum(x - mu)^2 / N
- Shannon Entropy: H(X) = -sum p(x) log p(x)

Applications:
We use these metrics to show that surprise 'quenches' variability (decreases FF) and increases the information gain per unit of time as the brain resolves the uncertainty caused by the omission.

Technical Code:
```python
import numpy as np
def calculate_kl_divergence(p, q):
    # p, q must be probability distributions
    p = np.array(p) + 1e-12
    q = np.array(q) + 1e-12
    return np.sum(p * np.log2(p / q))
```

References:
1. Cover, T. M., & Thomas, J. A. (2006). Elements of Information Theory. Wiley-Interscience.
2. Quian Quiroga, R., & Panzeri, S. (2009). Extracting information from neuronal populations: information theory and decoding approaches. Nature Reviews Neuroscience.
