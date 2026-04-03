# 🧬 OMISSION 2026: 15-Step LFP-NWB Analysis Pipeline

This document formalizes the LFP-only pipeline for Sequential Visual Omission Analysis, grounded in poster-standard findings (Low-frequency modulation, Beta/Alpha top-down signals).

## 1. NWB LFP Contract & Session Schema
- **Anchor**: Code 101.0 (Presentation-1 Onset).
- **Metadata**: Locate electrode table, coordinates, region labels, photodiode.
- **Output**: Canonical session dictionary (session_id, area, depth, trial_id, condition, signal).

## 2. Event Timeline & Omission Windows
- **Timeline**: fx -> p1 -> d1 -> p2/om -> d2 -> p3/om -> d3 -> p4/om -> d4 -> reward.
- **Concept**: Ghost Signal - identical gray-screen input, distinct predictive internal states.

## 3. LFP QC & Referencing
- **Bipolar**: Apply bipolar derivation to reduce volume conduction and reference contamination.
- **Metrics**: variance, line noise (60Hz), spatial contact quality.

## 4. Aligned LFP Epoch Extraction
- **Windows**: Centered on omission/stimulus onset.
- **Output**: [trials × channels × time] tensors.

## 5. Baseline Normalization
- **Standard**: Z-score relative to fixation baseline (0-1000ms) or percent change (dB).
- **Scale**: Fix consistent color limits across all hierarchical areas.

## 6. Time-Frequency Representations (TFR)
- **Method**: Multitaper spectral estimation or Wavelet (consistent across sessions).
- **Bands**: Theta (4-8), Alpha (8-13), Beta (15-25), Gamma (35-70).

## 7. Band Power Trajectories
- **Output**: Line graphs (Mean ± SEM) per band.
- **Contrast**: Omission minus matched-predictable stimulus windows.

## 8. Spectral Interaction Heatmaps
- **Logic**: Pairwise correlation of band power between all area pairs.
- **Visualization**: Triangular heatmaps showing synchrony spread (especially Beta).

## 9. Coherence Spectra
- **Method**: Frequency-resolved coupling for all area pairs.
- **Output**: "Omission minus Predictable" coherence difference curves.

## 10. Network Graphs
- **Nodes**: Cortical areas.
- **Edges**: Significant coherence differences (Red = Omission ↑, Blue = Control ↑).

## 11. Directed Connectivity (Granger)
- **Method**: Nonparametric Spectral Granger Causality.
- **Focus**: Weakening of bottom-up (Gamma) vs. Strengthening of top-down (Beta) during omission.

## 12. Statistically Corrected Comparisons
- **Tests**: Cluster-based permutation tests for TFR; Wilcoxon rank-sum for laminar/tier contrasts.

## 13. Hierarchical Gradients
- **Output**: "Hierarchy Profile" plots (Low-Order V1/V2 -> Mid -> High-Order FEF/PFC).

## 14. Trial-Progress & Adaptation
- **Focus**: Post-omission quenching.
- **Analysis**: Trajectories over trial index (1st, 2nd, 3rd post-omission trials).

## 15. Poster-Ready Packaging
- **Output**: Standardized panel set (Timeline, Spectrograms, Coherence Networks, GC Diagrams).
- **Manifest**: Reproducibility JSON linking figures to data arrays.

---
*Reference: user_lfp_plan_update_20260403*
