---
name: analysis-neuro-omission-unit-classification
description: "Omission analysis skill focusing on analysis neuro omission unit classification. Includes Top 10 S+/O+ indexing rules."
---

# Functional Unit Classification

We categorize neurons into distinct types based on their response profiles during stimulus presentations and omissions. This mapping is critical for proving hierarchical predictive coding.

## Categories
1. **S+ (Stimulus Prime)**: High response to visual input (p1), minimal response during omissions. (Peak in V1-V4).
2. **O+ (Omission Prime)**: Respond primarily when an expected stimulus is missing (p2). (Peak in FEF-PFC).
3. **S- / O-**: Suppressed units during stimulus or omission respectively.

## Ranking & Ground Truth (Top 10 Rule)
To establish ground truth in Figure 7 (SFC), we identify the **Top 10** neurons per area based on:
- **S+ Score**: Mean FR in `p1` (0-531ms) / Mean FR in `fx` (-500 to 0ms).
- **O+ Score**: Mean FR in `p2` (1031-1562ms) / Mean FR in `d1` (531-1031ms).

## Implementation
```python
fr_p1 = np.mean(spk[:, :, 1000:1531], axis=(0, 2))
fr_fx = np.mean(spk[:, :, 500:1000], axis=(0, 2))
s_plus_rank = fr_p1 / (fr_fx + 1e-5)
top_10_units = np.argsort(s_plus_rank)[-10:]
```

## Significance
The distribution of these types confirms the hierarchical nature of active inference: Stimulus-driven activity flows forward (Gamma), while Omission-driven activity (Prediction Error) flows across the higher-order Beta network.

References:
1. Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. Nature Neuroscience.
2. Bastos, A. M., et al. (2012). Canonical microcircuits for predictive coding. Neuron.
