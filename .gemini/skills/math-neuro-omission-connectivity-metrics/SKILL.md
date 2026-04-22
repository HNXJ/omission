---
name: math-neuro-omission-connectivity-metrics
description: Quantitative formalisms for functional connectivity, including Pairwise Phase Consistency (PPC), Spectral Harmony, and Granger Causality.
---
# skill: math-neuro-omission-connectivity-metrics

## When to Use
Use this skill when quantifying the interactions between different areas of the 11-area cortical hierarchy. It is mandatory for:
- Calculating Pairwise Phase Consistency (PPC) to assess Spike-Field Coupling (SFC) without trial-count bias.
- Measuring "Spectral Harmony" (cross-area power envelope correlations) in Beta and Gamma bands.
- Estimating directed connectivity (Feedforward vs. Feedback) using Granger Causality.
- Constructing global adjacency matrices for the Predictive Routing network.

## What is Input
- **Signal Pairs**: LFP-LFP or Spike-LFP pairs from two distinct recording sites.
- **Phase Estimates**: Instantaneous phases $(\theta)$ extracted via Hilbert Transform or Wavelet convolution.
- **Trial Groups**: Data categorized by condition (e.g., `S+`, `O+`).

## What is Output
- **Consistency Scores**: PPC values ranging from -1 to +1 (or 0 to 1 for magnitude).
- **Adjacency Matrices**: $11 \times 11$ heatmaps showing connectivity strength between areas.
- **Causality Indices**: Spectral Granger curves indicating frequency-dependent influence.

## Algorithm / Methodology
1. **Pairwise Phase Consistency (PPC)**: Calculated as $PPC = \frac{\sum_{i<j} \cos(\theta_i - \theta_j)}{\binom{N}{2}}$. This is the bias-free alternative to Phase Locking Value (PLV).
2. **Spectral Harmony**: Quantifies network-wide synchronization by correlating power envelopes across the hierarchy.
3. **Directed Influence**: FF influence (V1 -> PFC) is typically mapped to Gamma, while FB influence (PFC -> V1) is mapped to Beta.
4. **Granger Formalism**: $F = \ln(\text{Var}_{\text{restricted}} / \text{Var}_{\text{unrestricted}})$, measuring the reduction in prediction error.

## Placeholder Example
```python
import numpy as np

# 1. Compute PPC (Bias-Free SFC)
# sum_cos, sum_sin are sums over spikes of phase components
sum_w = np.sum(spikes)
sum_w2 = np.sum(spikes**2)
ppc = ((sum_cos**2 + sum_sin**2) - sum_w2) / (sum_w**2 - sum_w2)

# 2. Build Adjacency Matrix
adj_matrix = np.zeros((11, 11))
# Fill with cross-area PPC or Power Correlation
```

## Relevant Context / Files
- [lfp-core](file:///D:/drive/omission/.gemini/skills/lfp-core/skill.md) — For raw signal preparation.
- [src/math/connectivity.py](file:///D:/drive/omission/src/math/connectivity.py) — The library containing verified PPC and Granger implementations.
