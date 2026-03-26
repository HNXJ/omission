# Analysis Plan: Population Dynamics & Functional Categories

## 1. Unit Functional Classification (6,040 Neurons)
**Objective**: Catalog the computational roles of all neurons in the project.
- **Criteria**:
    - **Omit-Preferring**: Firing rate Omit > Delay (p < 0.05).
    - **Stim-Selective**: Significant difference (AUC > 0.6) between Stim A and Stim B.
    - **Transient vs Sustained**: Temporal decay of the surprise response.
- **Distribution**: 11-area map showing where the most "Prediction Error" (Omit+) units reside.

## 2. Population Manifold Analysis (PCA/UMAP)
**Objective**: Visualize the state-space trajectories of the internal model.
- **Dimensionality Reduction**: Principal Component Analysis (PCA) and Uniform Manifold Approximation (UMAP).
- **Metric**: Centroid Divergence Map.
- **Insight**: PCA reveals how the population "jumps" to a surprise-state manifold during omissions, distinct from the delay-state manifold.

## 3. Stability & Drift Analysis
**Objective**: Audit the temporal stability of the generative model.
- **Metric**: Representational Similarity Analysis (RSA) across trials.
- **Result**: Higher similarity = Lower drift = More precise prediction.
- **Comparison**: `RRRR` (Stochastic/Random) vs `AAAB` (Predictable) stability profiles.

## 4. Layer-Specific Mapping
**Objective**: Map the laminar distribution of omission signals.
- **Method**: Current Source Density (CSD) or Spike-Sorting Channel Depth relative to the LFP inversion point.
- **Result**: Identifying if Omit+ signals are concentrated in Granular (Infragranular/Supragranular) layers.
- **Hypothesis**: Top-down predictions in Infragranular layers; Prediction Errors in Supragranular layers.

## 5. Hub-Unit Dynamics
**Objective**: Track the high-information units identified in the Decoding phase.
- **Metric**: Participation Coefficient in the functional network.
- **Result**: Do high-information units also act as high-connectivity hubs?
- **Implication**: Identifies the "Master Clock" or "Contextual Hub" for expectation in the primate brain.
