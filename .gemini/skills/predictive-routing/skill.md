---
name: predictive-routing
description: Laminar LFP analysis, oculomotor controls, and statistical validation for the Predictive Routing paradigm. Covers CSD, JAX wavelet engine, microsaccade rejection, and GLM/permutation stats.
---

# skill: predictive-routing

## spectral decomposition & csd
- `compute_1d_csd`: Spatial Laplacian for Layer 4 identification.
- `compute_tfr_multiband`: JAX-vectorized Morlet wavelet engine (parallel multi-band).
- `subtract_erp`: Isolates induced power from phase-locked transients.
- **Source**: `predictive_routing_2020/src/spectral_analysis/`

## oculomotor controls & task logic
- `detect_microsaccades`: Engbert & Kliegl velocity-space thresholding (>30°/s).
- `get_clean_trials`: Purges microsaccade-contaminated epochs from analysis.
- `PredictiveRoutingTaskLogic`: Transition-probability state machine for sequence labels.
- **Source**: `predictive_routing_2020/src/preprocessing/oculomotor_controls.py`

## statistics & glm
- `run_permutation_test`: 2D cluster-based permutation testing for TFR clusters.
- `run_behavioral_regression`: GLM — regress reaction time against layer-specific power.
- `compute_wpli`: Weighted Phase Lag Index (volume-conduction-free inter-areal coherence).
- `compute_power_power_matrix`: Cross-frequency coupling between deep and superficial layers.
- **Source**: `predictive_routing_2020/src/statistics/`

## usage notes
- Use CSD before any layer-assignment or laminar split.
- Always apply `get_clean_trials` before TFR computation.
- FDR or cluster-based correction mandatory for all TFR/connectivity results.

## laminar protocol
1. Record with linear silicon probe (e.g., Neuropixels, 128ch).
2. Compute `compute_1d_csd` on average VEP to identify Layer 4 sink.
3. Assign channels to layers (supra/L4/infra) based on CSD zero-crossing.
4. Apply `subtract_erp` before TFR to isolate induced (non-phase-locked) power.

## connectivity protocol
1. Apply `get_clean_trials` — reject any trial with microsaccade >30°/s in analysis window.
2. Compute `compute_wpli` for each area-pair in each frequency band.
3. Apply FDR correction across all area-pairs.
4. Build adjacency matrix; compute betweenness centrality for hub identification.

## statistical thresholds
- Cluster-based permutation: 1000 permutations, α=0.05, cluster threshold t>2.0.
- FDR correction: Benjamini-Hochberg q<0.05 across frequency × area-pair comparisons.
- GLM β coefficient reported as standardized (z-scored predictors).
