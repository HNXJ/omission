# Master Plan: The Omission Hierarchy (V3)

## 🎯 Strategic Objective
A 4-Step, 4-Phase roadmap to quantify the cortical hierarchy of expectation using multi-scale neurophysiology and behavioral proxies. This plan prioritizes contextual decoding and high-resolution spectral coordination.

---

## 🏗️ Step 1: Classification & Behavioral Proxies (NEW)
**Objective**: Decode context and identity from neural and behavioral signals (Pupil/Eye).

### 🔄 Phases
1.  **Phase 1 (Signal Extraction)**: Align synchronized Pupil diameter and Eye-x-y gaze to P1 and Omission windows.
2.  **Phase 2 (Decoding Analysis)**: Binary classification of Omission Presence and Identity (A vs. B).
3.  **Phase 3 (Oddball vs. Repetition)**: Compare classification performance of repeated stimuli vs. sequence-discordant oddballs.
4.  **Phase 4 (Control Validation)**: Benchmark results against Fixation (FX), Inter-stimulus Delays (d1-d4), and Unpredictable Omission (RX).

### 🖼️ Figures
- **Figure 1**: Pupil Identity Decoder: A vs. B performance and divergence latency.
- **Figure 2**: Omission Decoder: Neural vs. Behavioral performance on detecting omissions.

---

## 🏗️ Step 2: Population Dynamics & Stability (DONE)
**Objective**: Establish the global response profile and the "Surprise Quenching" effect.

### 🔄 Phases (COMPLETED)
1.  **Phase 1 (Signal Extraction)**: Align 6,040 units to P1; baseline to fixation.
2.  **Phase 2 (Variability Mapping)**: Stabilized MMFF (150ms windows).
3.  **Phase 3 (Statistical Validation)**: Quenching magnitude across hierarchy (V1 -> PFC).

### 🖼️ Figures
- **Figure 3**: Grand Average Firing Rates per area (RRRR vs. Omissions).
- **Figure 4**: The Omission Response: selective population peaks during the 1531ms window.
- **Figure 5**: Hierarchical MMFF: Quenching of variability in post-omission stimuli.

---

## 🏗️ Step 3: Manifolds & Functional Categories (DONE)
**Objective**: Map the geometry of the internal model and the functional building blocks of error signaling.

### 🔄 Phases (COMPLETED)
1.  **Phase 1 (Latent Extraction)**: PCA/UMAP/t-SNE manifold projection of population activity.
2.  **Phase 2 (Functional Sorter)**: Categorize units (oxm+/-, stim+/-, null) via rule-based logic (+/- sigma).
3.  **Phase 3 (Topological Mapping)**: Project categories onto the low-dimensional manifold (v2 Centroids).

### 🖼️ Figures
- **Figure 6**: Unit Functional Categories across 11 areas (115 oxm+ neurons).
- **Figure 7**: Omission Manifolds: Identity separation (A vs. B) in state-space.
- **Figure 8**: Surprise Latency Hierarchy: Euclidean divergence timing across tiers.

---

## 🏗️ Step 4: Multi-Scale Connectivity & Coordination (TODO)
**Objective**: Quantify the mechanistic interaction between spikes and local rhythms.

### 🔄 Phases (SHIFTED)
1.  **Phase 1 (Spectral Decomposition)**: Extract band-specific power and phase for 6 target bands.
2.  **Phase 2 (Coordinative Metrics)**: Spike-LFP PLI and Spike-LFP Power Correlation.
3.  **Phase 3 (Graph Construction)**: 11x11 Granger Adjacency Matrix and CCG maps.

### 🖼️ Figures
- **Figure 9**: Spike-Spike CCG: Directional connectivity within area-pairs.
- **Figure 10**: Spike-LFP Power Correlation: Do spikes drive specific oscillatory bands?
- **Figure 11**: Spike-LFP PLI: Phase-locking of omission neurons to hierarchical rhythms.
- **Figure 12**: Cross-Band Hierarchy: Coordination of Gamma (Error) and Beta (Prediction).
- **Figure 13**: Summary Circuit Model: The Multi-Scale Omission Network.

---
*Plan established by Gemini CLI. Shifted for Step 1 Priority.*
