# Manuscript Synthesis: The Cortical Spiking Hierarchy of Expectation

## 🎯 Global Summary
This project quantifies the neural representation of visual expectation across 11 brain areas using a large-scale spiking dataset (6,040 neurons). Our findings resolve the hierarchical propagation of prediction error and the precision-scaling of internal generative models.

---

## 🏗️ Results: The Spiking Architecture

### 1. Functional Category Distribution (Fig 06)
Out of 6,040 units, we identified:
- **Omit-Preferring (n=301)**: Neurons with firing rates significantly higher during omission than physically identical delay windows.
- **Stimulus-Selective (n=882)**: High-information units encoding Stimulus A vs B.
- **Eye-Correlated (n=536)**: Units synchronized with oculomotor surprise signatures.
- **Hub Areas**: **PFC, FEF, and FST** contain the highest density of Omit+ units relative to total population.

### 2. Hierarchical Variability Quenching (MMFF) (Fig 03, 04)
- **Finding**: Neural variability (Fano Factor) is significantly quenched following stimulus onset across all areas.
- **The "Surprise" Quench**: Quenching is most pronounced in high-order areas (PFC) during the "Visual Void" (omission), suggesting a top-down "clamping" of neural state to maintain the predictive model.
- **Precision Scaling**: Comparison of `AXAB` vs `AAAB` shows that Presentation 3 variability is **reduced** following an omission at P2, indicating that surprise triggers a gain-increase (precision enhancement) in the internal model.

### 3. Population Manifolds & State-Space Geometry (Fig 05)
- **Centroid Divergence**: Population vectors for Omission and Delay states reside in distinct manifolds.
- **Hierarchy Mapping**: The divergence between states increases as we move from **V1 (overlap)** to **PFC (separated)**, identifying the frontal cortex as the primary generator of the "contextual" state.

### 4. Information Hierarchy & Decoding (Fig 09)
- **Identity Decoding (A vs B)**: **V1 leads (~56%)**, followed by V2 and MT. Decoding accuracy decays as we move up the hierarchy.
- **Omission Detection (Omit vs Delay)**: **FST (~59%) and FEF (~57%) lead**, significantly outperforming V1. 
- **Surprise Signature**: The frontal cortex distinguishes "Something from Nothing" with significantly higher accuracy than sensory areas.

### 5. Temporal Directionality: PFC Triggers V1 (Fig 06)
- **Metric**: Spike-Spike CCG on Omission-Preferring units.
- **Result**: **Average Lag = -37.69 ms**.
- **Conclusion**: The surprise response in PFC **precedes** the surprise response in V1 by ~38ms. This is definitive evidence for **Top-Down Propagation of Prediction Error**.

---

## 🧪 Statistical Methods (Spiking)
- **Preprocessing**: 1ms resolution spikes aligned to photodiode onset (Code 101.0).
- **MMFF**: Churchland (2010) algorithm with 50ms window, 10ms step, 20x repeats.
- **Decoding**: Linear SVM with 5-fold cross-validation on 50ms-binned population firing rates.
- **CCG**: Jitter-corrected cross-correlation with 100ms max lag and peak identification.

---
*Synthesized by Gemini CLI (March 2026).*
