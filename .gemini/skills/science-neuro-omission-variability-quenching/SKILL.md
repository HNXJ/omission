---
name: science-neuro-omission-variability-quenching
description: "Omission analysis skill focusing on science neuro omission variability quenching."
---

# Variability Quenching and Fano Factor (MMFF)

Neural variability quenching refers to the reduction in across-trial variance of neuronal firing following the onset of a stimulus or a cognitive event. This phenomenon is often quantified using the Fano Factor (FF = Variance / Mean). As described by Churchland et al. (2010, DOI: 10.1038/nn.2501), the onset of a stimulus 'tightens' the neural state stability, reducing stochastic noise.

Mean-Matched Fano Factor (MMFF):
Since FF is sensitive to changes in the mean firing rate, we use a Mean-Matching procedure. We calculate the distribution of means across all units and time points and subsample the units to ensure a constant mean distribution over time. This allows us to isolate the change in variability independent of firing rate changes.

In Omission Tasks:
A key hypothesis is that surprise (omission) triggers a stronger quenching effect on the *subsequent* stimulus. For example, the stimulus P3 following an omission (X in AXAB) should show lower MMFF (higher quenching) than P3 following a standard P2 (AAAB). This indicates that the brain increases its predictive precision (lowers uncertainty) after a surprise.

Technical Implementation:
```python
def compute_mmff(counts_matrix):
    # counts_matrix: (trials, time)
    import numpy as np
    mean = np.mean(counts_matrix, axis=0)
    var = np.var(counts_matrix, axis=0)
    fano = var / (mean + 1e-9)
    return fano

# Post-processing requires mean-matching across units
```

Scientific Context:
Quenching is thought to represent the transition from a high-entropy exploratory state to a low-entropy representational state. In Active Inference terms, this is the precision-weighting of sensory input.

References:
1. Churchland, M. M., et al. (2010). Stimulus onset quenches neural variability: a widespread cortical phenomenon. Nature Neuroscience.
2. Hussar, C. R., & Pasternak, T. (2010). Variability of Visual Responses. Journal of Neuroscience.
