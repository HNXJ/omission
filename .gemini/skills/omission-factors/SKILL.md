---
name: omission-factors
description: Extracts a high-dimensional feature matrix (48 factors per neuron) for dimensionality reduction and population dynamics analysis.
version: 1.0.0
---

# SKILL: Omission Neuron Factor Extraction

This skill provides the definitive framework for characterizing the firing dynamics and variability of every neuron recorded during the visual omission paradigm.

## 📊 Matrix Structure: 48 Factors
For each neuron, 4 core metrics are computed across 12 specific time intervals, resulting in a 48-factor feature vector.

### Core Metrics
1.  **`mean_fr`**: Average firing rate (Hz) computed from binary spike counts.
2.  **`std_isi`**: Standard deviation of Inter-Spike Intervals (ms), characterizing firing regularity.
3.  **`mean_var`**: Average across-trial variance, characterizing neural variability.
4.  **`std_var`**: Standard deviation of the across-trial variance trace, characterizing variability volatility.

### Time Intervals (12 Total)
- **Fixation**: `fx` window for conditions `RXRR`, `RRXR`, `RRRX`.
- **Pre-Omission Delay**: `d1`, `d2`, or `d3` windows depending on the condition.
- **Omission window ("X")**: `p2`, `p3`, or `p4` windows depending on the condition.
- **Post-Omission Delay**: `d2`, `d3`, or `d4` windows depending on the condition.

## 🧬 Metadata
The resulting matrix (`omission_neurons_r_factors.csv`) includes essential spatial and laminar context:
- `session`: The 6-digit session identifier.
- `area`: The mapped brain area (e.g., V1, PFC, MT).
- `channel`: The relative electrode ID within the probe (0-127).
- `layer`: The spectro-laminar position (`Deep`, `Superficial`, or `none`).

## 🛠️ Usage Examples

### PCA / UMAP Visualization
```python
import pandas as pd
import umap
from sklearn.decomposition import PCA

df = pd.read_csv('checkpoints/omission_neurons_r_factors.csv')
features = df.filter(regex='_mean_|_std_')

# PCA
pca = PCA(n_components=3).fit_transform(features)

# UMAP
reducer = umap.UMAP(n_components=3)
embedding = reducer.fit_transform(features)
```

## 🔬 Scientific Context
This extraction logic is grounded in Hierarchical Predictive Coding and Stimulus-Driven Variability Quenching (Churchland et al., 2010). The inclusion of ISI and variability metrics allows for the dissociation of mean rate changes from changes in neural state stability.
