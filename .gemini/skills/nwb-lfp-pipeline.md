# Skill: nwb-lfp-pipeline (15-Step Standard)

## Description
A comprehensive LFP-only analysis pipeline for Sequential Visual Omission tasks. Designed to replicate poster-style spectral and connectivity findings (Beta synchrony, top-down feedback).

## The 15 Steps
1.  **NWB Schema Reader**: Standardize metadata (Code 101.0 anchor).
2.  **Timeline Rebuilder**: Reconstruct predictable vs omission windows.
3.  **Bipolar Referencing**: Subtraction of adjacent channels to isolate local field.
4.  **Epoch Extraction**: Align LFP to omission/stimulus onsets.
5.  **Baseline Normalization**: Z-score or dB change relative to fx (0-1000ms).
6.  **TFR Multitaper Engine**: High-resolution spectral estimation.
7.  **Band Trajectories**: Mean ± SEM traces for Theta, Alpha, Beta, Gamma.
8.  **Spectral Interaction Heatmaps**: Pairwise power correlation across areas.
9.  **Coherence Spectra**: Frequency-resolved inter-areal coupling.
10. **Network Graphs**: Visualization of significant coherence differences.
11. **Granger Causality**: Directed spectral interactions (FF vs FB).
12. **Cluster Statistics**: Nonparametric correction for TFR maps.
13. **Hierarchical Gradients**: Profiles across Low, Mid, and High cortical tiers.
14. **Post-Omission Adaptation**: Trial-by-trial quenching analysis.
15. **Poster-Ready Export**: Packaging figures with reproducibility manifests.

## Code Standard
```python
# Bipolar Step (Step 3)
def compute_bipolar(lfp):
    return lfp[:, :-1, :] - lfp[:, 1:, :]

# Hierarchy Tiers (Step 13)
TIERS = {'Low': ['V1', 'V2'], 'Mid': ['V4', 'MT'], 'High': ['FEF', 'PFC']}
```

## Mandatory Theory
- **Ghost Signal**: Identical sensory input must yield divergent neural states if an internal model exists.
- **Beta (15-25Hz)**: The primary carrier of omission-related predictive feedback.
- **Gamma (35-70Hz)**: Feedforward sensory drive, often stable during omission.
