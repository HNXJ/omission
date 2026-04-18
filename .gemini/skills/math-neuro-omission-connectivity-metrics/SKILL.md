---
name: math-neuro-omission-connectivity-metrics
description: "Omission analysis skill focusing on math neuro omission connectivity metrics. Includes PPC and Spectral Harmony."
---

# Connectivity Metrics & Formalisms

Quantitative definitions for connectivity analysis allow for objective assessment of network interactions across the 11-area visual hierarchy.

## 1. Pairwise Phase Consistency (PPC)
A bias-free measure of spike-field coupling (SFC). 
Formula: $PPC = \frac{\sum_{i<j} \cos(\theta_i - \theta_j)}{\binom{N}{2}}$
Where $\theta_i$ is the LFP phase at the time of spike $i$. 
Use PPC to quantify how strongly S+ or O+ neurons lock to rhythmic LFP oscillations without being biased by trial count or firing rates.

## 2. Spectral Harmony (Cross-Area Correlation)
We quantify "network harmony" by correlating the power envelopes of specific bands (Beta or Gamma) across all 11 areas.
- **Gamma Harmony**: Dominates during stimulus presentation (Feedforward).
- **Beta Harmony**: Dominates during stimulus omission (Feedback).

## 3. Granger Causality (F)
$F = \ln(\text{Var}_{\text{restricted}} / \text{Var}_{\text{unrestricted}})$. 
Quantifies the reduction in prediction error of area Y when area X is included.

## Adjacency Matrices
We represent the 11-area network as a matrix $A$ where $A_{ij}$ is the connectivity strength (PPC or Power Correlation) from source $j$ to target $i$.

Implementation:
```python
# PPC Core Snippet
sum_cos = np.sum(spk * np.cos(phase))
sum_sin = np.sum(spk * np.sin(phase))
sum_w = np.sum(spk)
sum_w2 = np.sum(spk**2)
ppc = ((sum_cos**2 + sum_sin**2) - sum_w2) / (sum_w**2 - sum_w2)
```

References:
1. Vinck, M., et al. (2010). The pairwise phase consistency: a bias-free measure of rhythmic neuronal synchronization. NeuroImage.
2. Bastos, A. M., & Schoffelen, J. M. (2015). A Tutorial Review of Functional Connectivity Analysis Methods. Frontiers in Systems Neuroscience.
