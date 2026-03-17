---
name: nwb-analysis
description: Enriched neurophysiology analysis suite for visual omission paradigms, including manifolds, variability, and connectivity.
version: 2.0.0
---

# SKILL: Enriched NWB Analysis Suite (nwb-actions)

This skill provides a unified codebase for high-fidelity neuro-analysis of the Visual Omission Oddball paradigm.

## ⏱️ Task Timing & Alignment (1000Hz)
Standard alignment is to the **onset of P1 (Code 101.0)**.
- **Fixation (`fx`)**: 0 to 1000ms.
- **Stimulus Window**: 531ms duration (e.g., p1: 1000-1531ms).
- **Delay Window**: 500ms duration (e.g., d1: 1531-2031ms).
- **Omission Windows**: 
    - `p2`: 2031-2562ms (RXRR)
    - `p3`: 3062-3593ms (RRXR)
    - `p4`: 4093-4624ms (AAAX)

## 🔬 Core Analysis Modules

### 1. Population Manifolds (48-Factor Matrix)
Extracts a high-dimensional feature vector per neuron across 12 intervals and 4 metrics (Mean FR, Regularity, Mean Variability, Variability Volatility).
- **Usage**: Dimensionality reduction (PCA/UMAP) to visualize population state trajectories.

### 2. Functional Categorization
Classifies neurons into mutually exclusive groups:
- **Omit**: Selective peak during omission windows (>2 SD above baseline).
- **Fix**: Selective activity during the fixation window (>50% drop during stimulus).
- **Stim+ / Stim-**: Robust positive or negative stimulus responses.

### 3. Refined Neural Variability (MMFF)
Computes the Mean-Matched Fano Factor (Churchland 2010) with optimized smoothing to navigate the bias-variance tradeoff:
- **Sliding Window ($W$)**: Use $W=100$ms (instead of 50ms) to increase the mean spike count per bin and reduce sampling error.
- **Step Size ($\Delta t$)**: Use $\Delta t=5$ms (instead of 10ms) to increase sampling density and temporal resolution.
- **Post-hoc Smoothing**: Apply a 1D Gaussian filter ($\sigma \approx 2-5$ units) to the *final* Fano factor trace. This preserves the raw statistical distributions required for Mean-Matching while providing a visually smooth result.
- **Baselining**: Hard-aligned to 0 during the -500ms to 0ms fixation window.

### 4. Directionality & Connectivity
Formal testing of regional interactions (e.g., V1 vs. PFC):
- **Lag Analysis**: Spike-spike cross-correlation to determine lead/lag timing.
- **Spectral Coordination**: LFP phase-lag and Granger Causality to dissociate FF (Gamma) from FB (Beta) signals.

## 🧬 Metadata Standards
- **Probe Rule**: 128 channels per probe.
- **Mapping**: DP -> V4; V3 -> V3d/V3a (50/50 split).
- **Indexing**: Handles NWB Global to .npy Local index translation.
