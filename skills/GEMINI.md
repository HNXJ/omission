# Omission Project Skills

## Scientific Analysis

### science-neuro-omission-predictive-routing
Analysis of latency, feedback/feedforward propagation, and hierarchy-wide omission responses. 
- **Theoretical Framework**: Active prediction errors routed across cortical laminæ (superficial: prediction errors up; deep: predictions down).
- **Goal**: Demonstrate omission responses are not just lack of sensory drive, but active prediction errors.

### analysis-neuro-omission-sfc-manifold
Coupling manifold dimensionality of spiking activity with LFP phase. 
- **Spike-Field Coupling (SUA x LFP)**: Selective phase-locking of "Omission Neurons" to specific rhythms (e.g., beta or theta) during the omission window, while non-relevant neurons are suppressed.
- **Metric Rigor**: Requires spike-count correction (e.g., Pairwise Phase Consistency, PPC) to prevent statistical artifacts during sparse omission windows.

### analysis-neuro-omission-cell-type-dynamics
Canonical putative classification based on multi-metric clustering (waveforms, firing rates, adaptation). 
- **Functional Clusters**: Stimulus-driven, prediction-driven, and omission-responsive units.
- **Laminar Mapping**: Mapping units to superficial, granular, and deep layers based on Current Source Density (CSD) profiles.

## Coding & Infrastructure

### coding-neuro-omission-automated-testing
Suite for validating pipeline data contracts, shape consistency, and NWB-table parsing.
- **Validation**: Ensures data mapped to CSD profiles correctly assigns units/LFP to layers.
- **Consistency**: Pipeline data contracts and table parsing logic.

## Design & Visualization

### design-neuro-omission-publication-figures
Automation of publication-ready, multi-panel figure generation with consistent thematic guidelines. 
- **Structure**:
    - **Figure 1: Paradigm and Theoretical Grounding**: Recording sites (128-channel laminar probe), CSD map, Task design (rhythmic vs. random control), and conceptual HPC model.
    - **Figure 2: Local Network Responses**: Representative PSTHs/rasters, layer-specific TFR spectrograms, and high-gamma power comparison (superficial vs. deep).
    - **Figure 3: Population State-Space Dynamics**: 3D manifold trajectories (PCA/jPCA), trajectory divergence (expected stimulus vs. omission), and cross-condition generalization distances.
    - **Figure 4: Inter-areal / Laminar Rhythm Coordination**: Band-specific dynamics (theta, alpha, beta, gamma), Spike-Field Coherence (SFC/PPC) polar plots, and binding mechanism summary.
