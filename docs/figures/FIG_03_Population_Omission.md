# FIG_03: Population Dynamics of the Omission Response

## 🎯 Intent
To demonstrate that omissions trigger reliable, hierarchical neural activity that mirrors stimulus-driven dynamics but in the absence of physical input.

## 🔬 Methodology
- **Source**: `src/f003_surprise/analysis.py`
- **Metric**: Population PSTH (Z-scored) and Omission Index ($OI = (R_{omit} - R_{base}) / (R_{omit} + R_{base})$).
- **Alignment**: Time-locked to omission onset (P2 position).
- **Statistics**: Wilcoxon Signed-Rank test vs. baseline.

## 📊 Observations
- Widespread response: >60% of units show significant modulation during omission.
- Hierarchical scaling: Omission response magnitude increases in higher cortical areas (PFC/FEF).
- Latency: Omission response onset is slightly delayed (~20-30ms) relative to the stereotypical stimulus response.

## 📝 Caption & Labels
**Figure 3. Hierarchical Scaling of the Neural Omission Response.**
(A) Grand average PSTH for all cortical areas aligned to omission.
(B) Distribution of Omission Indices ($S_k$ tiers indicated).
(C) Onset latency gradients across the hierarchy.

## 🗺️ Narrative Context
Leads to **FIG_04**, which uses dimensionality reduction to interrogate the structure of these representations.
