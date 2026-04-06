# Roadmap: Phase 3 – Deep LFP & Spike-Field Analysis

## 🎯 Strategic Objective
To characterize the oscillatory fingerprints of the "Visual Void" and map the multi-scale coordination between local field potentials (LFP) and single-unit activity (SPK) across the cortical hierarchy. This phase will expand the paper by 10+ figures, focusing on spectral power, phase dynamics, and cross-regional connectivity.

---

## 🔬 Core Analytical Framework

### 1. Spectral Band Definitions
All analyses will utilize standardized frequency bands:
- **Theta ($\theta$):** 4–8 Hz
- **Alpha ($\alpha$):** 8–14 Hz
- **Beta ($\beta$):** 15–30 Hz
- **Low Gamma ($\gamma_L$):** 35–55 Hz
- **High Gamma ($\gamma_H$):** 65–100 Hz

### 2. Time-Frequency Logic
- **Tools:** Complex Morlet Wavelets (7 cycles) or Multi-taper decomposition.
- **Normalization:** 
    - **Relative Change:** $P_{relative}(t, f) = \frac{P_{omit}(t, f)}{P_{delay}(t, f)}$.
    - **Baseline Correction:** Decibel change ($10 \cdot \log_{10}$) relative to the -500 to 0ms fixation window.

---

## 📈 Planned Figure Suite (Figures 7–16+)

### 🖼️ Figure 7: Spectral Fingerprints of Omission
**Goal:** Identify which frequency bands carry the omission signal in each tier of the hierarchy.
- **7A:** Time-Frequency Representations (TFR) for Standard vs. Omission per area.
- **7B:** Power Spectrum Density (PSD) comparison during the `p4` window.
- **7C:** Relative Power Change Map (Omission / Delay) for all 11 areas.

### 🖼️ Figure 8: The Hierarchy of Gamma Bursts
**Goal:** Quantify the magnitude and timing of Gamma oscillations as a proxy for prediction error.
- **8A:** Band-pass filtered Gamma traces (40–80 Hz) for visual vs. executive areas.
- **8B:** Latency of Gamma peak relative to omission onset across areas.
- **8C:** Correlation between Gamma power and Omission Neuron firing rates.

### 🖼️ Figure 9: Beta-Band Prediction Maintenance
**Goal:** Test if Beta oscillations reflect the top-down maintenance of the internal model.
- **9A:** Beta-band power trajectories during `d3-p4-d4`.
- **9B:** Comparison of Beta quenching during Standard vs. Omission.
- **9C:** PFC dominance in Beta power relative to sensory areas.

### 🖼️ Figure 10: Phase-Amplitude Coupling (PAC)
**Goal:** Determine if low-frequency phase (Alpha/Beta) modulates high-frequency error signals (Gamma).
- **Metric:** Modulation Index (MI) calculated via the Tort et al. method.
- **10A:** Comodulograms showing Phase (8–30Hz) vs. Amplitude (40–100Hz) coupling.
- **10B:** Omission-specific increases in PAC across the hierarchy.

### 🖼️ Figure 11: Spike-LFP Phase Locking
**Goal:** Measure the synchronization of "Real" Omission Neurons to local rhythms.
- **Metric:** Pairwise Phase Consistency (PPC) to rule out firing rate bias.
- **11A:** Spike-LFP coherence spectra for each area.
- **11B:** Preferred phase of firing relative to Gamma and Beta cycles.

### 🖼️ Figure 12: Cross-Frequency Correlations
**Goal:** Map the interactions between different spectral bands (e.g., does Alpha drop when Gamma rises?).
- **12A:** Correlation matrices between band-limited power traces.
- **12B:** Hierarchy of Band-Interaction: does spectral coordination emerge earlier in high-order areas?

### 🖼️ Figure 13: Inter-Regional Phase Coordination (PLI)
**Goal:** Quantify functional connectivity between area-pairs (e.g., V1-V4, MT-MST, FEF-PFC).
- **Metric:** Weighted Phase-Lag Index (wPLI) to ensure robustness against volume conduction.
- **13A:** wPLI adjacency matrices for Alpha, Beta, and Gamma bands.
- **13B:** Coordination strength as a function of anatomical distance.

### 🖼️ Figure 14: Network Granger Graphs
**Goal:** Visualize the full directional graph of information flow during omission.
- **Method:** Pairwise-conditional Granger Causality across all 11 areas.
- **14A:** 11x11 Granger Adjacency Matrix (FF vs FB bands).
- **14B:** Centrality analysis: which area is the primary "Hub" of omission signaling?

### 🖼️ Figure 15: Laminar Spike-Field Interactions
**Goal:** Resolve the layer-specific coordination of error and prediction.
- **15A:** Deep-layer Omission Neuron locking to Deep-layer Beta.
- **15B:** Superficial-layer Gamma locking to Deep-layer spikes.

### 🖼️ Figure 16: Mutual Information & Nonlinear Connectivity
**Goal:** Capture non-linear interactions that Granger/Coherence might miss.
- **Metric:** Time-resolved Transfer Entropy or Mutual Information between SPK and LFP.
- **16A:** Mapping of information flow during the 1531ms contextual window.

---

## 🛠️ Implementation Protocols

### Phase 1: Filtering & Enveloping
- Implement zero-phase forward-reverse FIR filters for each band.
- Extract analytic signals using the Hilbert Transform for phase and envelope calculation.

### Phase 2: Time-Frequency Extraction
- Utilize the `nitime` or `scipy.signal` wavelet implementations.
- Perform trial-shuffling to establish statistical significance thresholds for TFR maps.

### Phase 3: Connectivity Engine
- Develop a vectorized "Area-Pair Engine" to iterate through all 55 unique area combinations (11C2) within each session.
- Apply Multiple Comparison Correction (FDR or Cluster-based permutation) across frequencies and time points.

---
*Roadmap established by Gemini CLI. Ready for Directive: Execute Figure 7 (Spectral Fingerprints).*
