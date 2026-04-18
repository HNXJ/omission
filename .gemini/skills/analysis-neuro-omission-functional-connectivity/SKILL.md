---
name: analysis-neuro-omission-functional-connectivity
description: "Omission analysis skill focusing on analysis neuro omission functional connectivity. Includes Spectral Harmony and PPC."
---

# Functional Connectivity: Coordination & Harmony

Functional connectivity measures the synchronization between different brain areas, revealing the network-level coordination during stimulus and omission.

## 1. Spectral Harmony (Cross-Area Correlation)
Instead of raw coherence, we quantify coordination using **Cross-Area Power Envelope Correlations**.
- **Gamma Harmony**: Dominant inter-area coordination during stimulus presentation (Feedforward flow).
- **Beta Harmony**: Dominant inter-area coordination during stimulus omission (Feedback Prediction Error).
- **Analysis**: 11x11 Pearson correlation matrices of band-specific power envelopes during the omission window.

## 2. Pairwise Phase Consistency (PPC)
The preferred metric for Spike-Field Coupling (SFC). 
- Bias-free regarding trial count and firing rate.
- Used to contrast the phase-locking of S+ neurons (during stimulus) and O+ neurons (during omission).

## 3. Directionality
Directional influence is inferred from the hierarchical lag and spectral profile. 
- Higher-order areas (PFC/FEF) drive the **Beta Omission Response** down the hierarchy.
- Lower-order areas (V1-V4) drive the **Gamma Stimulus Response** up the hierarchy.

## Implementation (Figure 8)
```python
# Correlation of envelopes
corr_mat = np.corrcoef(power_envelopes_matrix) # 11 x 11
```

References:
1. Vinck, M., et al. (2010). The pairwise phase consistency: a bias-free measure of rhythmic neuronal synchronization. NeuroImage.
2. Bastos, A. M., et al. (2015). Visual areas exert feedforward and feedback influences through distinct frequency channels. Neuron.
