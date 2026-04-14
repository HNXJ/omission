# Omission Project Skills: Comprehensive Inventory

This document inventories the specialized skills and knowledge domains required for the Omission project. These skills represent the agentic capabilities used to navigate, analyze, and build the repository.

## 🔬 Scientific Analysis & Domain Knowledge

### science-neuro-omission-predictive-routing
Analysis of latency, feedback/feedforward propagation, and hierarchy-wide omission responses. 
- **Theoretical Framework**: Active prediction errors routed across cortical laminæ (superficial: prediction errors up; deep: predictions down).
- **Goal**: Demonstrate omission responses are not just lack of sensory drive, but active prediction errors.

### science-neuro-omission-ghost-signals
Identification and quantification of internal generative signals (ghost signals) that persist in the absence of sensory input.

### science-neuro-omission-active-inference
Application of Active Inference principles (e.g., Precision Scaling) to neural and oculomotor quenching.

### Functional Domains:
- **science-neuro-omission-cortical-hierarchy**: Mapping responses across V1 to PFC.
- **science-neuro-omission-identity-coding**: Decoding stimulus identity from "ghost" responses.
- **science-neuro-omission-spectral-fingerprints**: identifying frequency-specific coordination modes.
- **science-neuro-omission-surprise-latencies**: Measuring the timing of unexpectedness signals.
- **science-neuro-omission-variability-quenching**: quantifying Fano Factor reduction.

## 📊 Neural Analysis & Mathematics

### analysis-spectrolaminar
Methodology for mapping Current Source Density (CSD) to detect L4 crossovers and assign units to superficial/granular/deep layers.

### Math & Connectivity:
- **math-neuro-omission-connectivity-metrics**: Granger Causality, Coherence, and PDC.
- **math-neuro-omission-stochastic-metrics**: Fano Factor, MMFF, and variance normalization (MMV).
- **analysis-neuro-omission-pac-analysis**: Phase-Amplitude Coupling shifts during surprise.
- **analysis-neuro-omission-population-manifolds**: PCA/UMAP/jPCA trajectories in state-space.
- **analysis-neuro-omission-unit-classification**: Clustering units based on response polarity (S+/-, O+/-).

### analysis-neuro-omission-sfc-manifold
Coupling manifold dimensionality of spiking activity with LFP phase using metrics like Pairwise Phase Consistency (PPC).

## 💻 Coding & Computational Infrastructure

### coding-neuro-omission-nwb-pipeline
Orchestration of the 15-step LFP-NWB analysis protocol, ensuring data contracts and schema validation.

### coding-neuro-omission-decoding-engine
Implementation of Linear SVM classifiers for the 108-test hypothesis matrix.
- **coding-neuro-omission-signal-conditioning**: Baseline normalization (dB), smoothing (Gaussian), and artifact pruning.

### Frameworks & Tools:
- **jax-actions / jaxley-actions**: High-performance gradient-accelerated computing for connectivity matrices.
- **system-nwb-metadata**: Direct interaction with HDF5 metadata for deterministic area mapping.
- **coding-neuro-omission-bhv-parser**: Integration of MonkeyLogic behavioral data.

## 🎨 Design & Visualization

### design-neuro-omission-publication-figures
Automation of publication-ready, multi-panel Plotly figure generation (The "Golden Standard").
- **Structure**: Consistent thematic guidelines (Arial/Helvetica, ±SEM patches, pink omission windows).

### Specialized Visualization:
- **design-neuro-omission-advanced-plotting**: TFR heatmaps, network adjacency graphs, and 3D manifold animations.
- **design-neuro-omission-branding-theme**: Implementation of the Madelane Golden Dark palette.
- **poster-figures**: Synthesis of analysis results into high-density poster layouts.

## 🛠️ Operations & Management

### github-management-actions
Mandatory Commit-Pull-Push safety workflow and scoped repository management.

### system-area-audit
Validation of probe-to-area mapping across all 13 sessions using NWB-metadata source-of-truth.

### study-eval-actions / bridger-actions
Methods for evaluating pipeline health, reproducibility logs, and agentic hand-off protocols.

---
*Note: This list is dynamically updated based on the `audit_skills_list.md` inventory.*
