# Comprehensive Omission Analysis Plan: The Cortical Hierarchy of Expectation

## 🎯 Strategic Objective
To quantify the cortical hierarchy of expectation using multi-scale neurophysiology, characterizing the oscillatory fingerprints of the "Visual Void" and mapping the multi-scale coordination between local field potentials (LFP) and single-unit activity (SPK) across 11 brain areas. This plan integrates population dynamics, manifold geometry, and spectral coordination to resolve layer-specific mechanisms of error and prediction.

---

## 🔬 Core Analytical Framework

### 1. Standardized Frequency Bands
- **Theta ($\theta$):** 3–8 Hz
- **Alpha ($\alpha$):** 8–14 Hz
- **Beta ($\beta$ / $\beta_1, \beta_2$):** 13–32 Hz (Focus: Top-down predictive signals)
- **Low Gamma ($\gamma_L$):** 35–60 Hz (Focus: Feedforward prediction error)
- **High Gamma ($\gamma_H$):** 60–150 Hz

### 2. Time-Frequency & Signal Logic
- **Tools:** Complex Morlet Wavelets (7 cycles) or Multi-taper decomposition.
- **Normalization:** Relative Power Change ($P_{omit} / P_{delay}$) or Decibel change relative to fixation (-500 to 0ms).
- **Robustness Rule:** Within-session analysis for all connectivity/coordination metrics to ensure biological validity.

---

## 🏗️ Phased Roadmap

### Step 1: Classification & Behavioral Proxies (Figures 1–4) [✅ COMPLETED]
**Objective:** Establish the global response profile, stimulus identity decoding, and the "Surprise" signature.
- **Figure 1: Grand Average Firing Rates**: Compare Standard (RRRR) vs. Omission across 11 areas.
- **Figure 2: Pupil & Eye Decoding**: Quantify behavioral surprise using balanced 50/50 SVM.
- **Figure 3: Neural Identity Decoding**: V1-population decoding of Stim A vs. B (~62% acc).
- **Figure 4: Omission Detection (Omit vs. Delay)**: Rigorous within-trial contrast of physically identical windows (~55% acc).
- **Figure 4b: Oddball Effect**: V1 distinguishing P4 (Oddball) from P2/P3 (Repeated).

### Step 2: Population Dynamics & Stability (Figures 5–7) [✅ COMPLETED]
**Objective:** Map the quenching of variability and the geometry of the internal model.
- **Figure 5: Mean-Matched Fano Factor (MMFF)**: Hierarchical quenching of neural variability following surprise onset.
- **Figure 6: Unit Functional Categories**: Classification of 6,040 neurons (oxm+, stim+, stim-, null).
- **Figure 7: Population Manifolds (PCA/UMAP/tSNE)**: 3D state-space trajectories with Rainbow Hierarchy (V1 $\to$ PFC) and centroid-divergence maps.

### Step 3: Latency Hierarchy & Information Hubs (Figures 8–9) [✅ COMPLETED]
**Objective:** Resolve the temporal propagation of error and identify high-information units.
- **Figure 8: Surprise Latency Hierarchy**: Evidence for **Top-Down Propagation** (PFC 50ms $\to$ V1 49ms) during omission, reversing the sensory feedforward (V1 10ms $\to$ PFC 93ms) hierarchy.
- **Figure 9: Individual Information Mapping**: Decoding accuracy for 6,040 single neurons and 128 LFP channels independently to identify laminar/area hubs.

### Step 4: Multi-Scale Connectivity & Coordination (Figures 10–14) [✅ COMPLETED]
**Objective:** Resolve the mechanistic coordination between spikes and regional rhythms.
- **Figure 10: Spectral Fingerprints (Spectrograms)**: Gamma-band (60-90Hz) bursts selective to the omission window.
- **Figure 11: Phase-Amplitude Coupling (PAC)**: Theta-Gamma Modulation Index (MI) shifts during surprise.
- **Figure 12: Inter-Regional Coordination (Coherence)**: Surge in PFC-V1 Gamma Coherence (0.62) during the Visual Void.
- **Figure 13: Spike-LFP Phase Locking (PPC)**: Preference of omission neurons for local and distant rhythms.
- **Figure 14: Network Adjacency Matrices**: 11x11 maps of Spike-LFP, LFP-LFP, and Amp-Amp coordination.
- **Figure 15: Laminar Directionality**: V1-PFC Spike-Spike CCG and Spectral Granger (FF vs. FB).

### Step 5: Behavioral Proxies & Decoding (Figures 16–17) [✅ COMPLETED]
**Objective:** Characterize the behavioral signatures of the internal model using eye movements and pupil dynamics.
- **Figure 16: Eye-Movement Identity Decoding**: 3-Class decoding (A-Std, A-Omit, B-Omit) using high-dimensional features (x, y, v, a). [~67% Identity Acc].
- **Figure 17: Systematic Content Decoding**: Determining if the oculomotor system encodes the current visual content across 13 sessions.
    - **Global Decoding (Fix vs. Stim vs. Grey)**: ~60.2% accuracy (Chance 33%).
    - **Specific Decoding (5-Class)**: ~41.6% accuracy (Chance 20%).
- **Feature Contribution**: Gaze Position (Pos) is the primary driver, followed by Pupil diameter and Kinetics.
- **Conclusion**: Eye movements are not passive during fixation; they systematically reflect both stimulus content and internal expectations.

---

## 🔬 Specific Analytical Deep-Dives

### V1 vs. PFC Directionality Analysis
- **Objective**: Characterize the causal interaction during visual omission windows.
- **Causal Hypothesis**: Gamma (FF) dominance for V1 -> PFC; Beta (FB) dominance for PFC -> V1.
- **Metrics**: Spike-Spike CCGs (Lag Analysis) and LFP-LFP Spectral Granger Causality (`nitime`).

### High-Fidelity Visualizations
- **Condition-Specific Profiles**: RRRR (Brown), RXRR (Red), RRXR (Blue), RRRX (Green).
- **MUA Activity Profiles**: Aggregated probe-level spiking to supplement single-unit data.
- **Advanced Granger Layouts**: 4-subplot diagrams including Direction Graphs and Strength-Time/Freq plots.

---

## 🛠️ Implementation Protocols

1. **Filtering & Enveloping**: Zero-phase FIR filters + Hilbert Transform for phase/envelope.
2. **Connectivity Engine**: Vectorized "Area-Pair Engine" to iterate through all 55 unique area combinations per session.
3. **Statistical Refinement**: Multiple Comparison Correction (FDR/Cluster-based permutation) for all TFR and connectivity maps.
4. **Paper-First Workflow**: Transcription of figure manifests into Methods and Results sections as figures are finalized.

---

## 🚀 Manuscript & Deployment Goals
- **Manuscript Drafting**: Build the "Source of Truth" from figure manifests (`docs/figures/FIG_XX.md`).
- **Remote Deployment**: Automate SSH login and launch Qwen 3.5 MLX server at `10.32.133.50` for advanced reasoning tasks.

---
*Synthesized Omission Analysis Plan established by Gemini CLI.*
