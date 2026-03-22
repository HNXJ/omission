# Functional Unit Classification

We categorize neurons into distinct types based on their response profiles during stimulus presentations and omissions. This allows us to map the functional architecture of the hierarchy.

Categories:
1. Stimulus-Driven: High response to A and/or B, minimal response during omissions. (Common in V1/V2).
2. Omission-Specific: Respond only or primarily when an expected stimulus is missing. (Surprise neurons, common in PFC).
3. Context-Sensitive: Respond to both stimulus and omission, but with different temporal profiles or magnitudes. (Predictive coding units).
4. Tonic/Baseline: No significant change across conditions.

Criteria:
- Stimulus Index: (FR_stim - FR_base) / (FR_stim + FR_base).
- Omission Index: (FR_omit - FR_stim) / (FR_omit + FR_stim).
- Latency: Timing of the peak response.

Technical Implementation:
```python
def classify_unit(fr_stim, fr_omit, fr_base):
    if fr_stim > fr_base * 2 and fr_omit < fr_base * 1.5:
        return 'Stimulus-Driven'
    if fr_omit > fr_base * 2 and fr_stim < fr_base * 1.5:
        return 'Omission-Specific'
    return 'Other'
```

Significance:
Understanding the distribution of these types across areas (e.g., more Omission-Specific in FEF than V4) confirms the hierarchical nature of active inference.

References:
1. Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. Nature Neuroscience.
2. Keller, G. B., & Mrsic-Flogel, T. D. (2018). Predictive Processing: A Canonical Cortical Computation. Neuron.
