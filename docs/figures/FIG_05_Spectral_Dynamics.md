# FIG_05: Spectral Power Dynamics (TFR)

## 🎯 Intent
To visualize the broadband spectral fingerprints of the omission response, identifying distinct frequency bands (Beta, Gamma) associated with predictive routing.

## 🔬 Methodology
- **Source**: `src/f005_tfr/analysis.py`
- **Method**: Multitaper Time-Frequency Representation (TFR).
- **Parameters**: 
    - Frequency range: 4-100Hz.
    - Time window: -2000 to 2000ms aligned to omission.
    - Normalization: dB-baseline corrected (-1000 to -500ms).

## 📊 Observations
- Beta Suppression: Predictable suppression of beta power (15-25Hz) following omission onset.
- Gamma Burst: Transient increase in gamma power (40-80Hz) specifically in superficial layers during the omission window.
- Hierarchical Scaling: The magnitude of the spectral modulation increases along the V1-PFC axis.

## 📝 Caption & Labels
**Figure 5. Spectral Fingerprints of the Omission Response.**
(A) Population-averaged TFR heatmaps for V1 and PFC during standard sequence (AAAB) and Omission (AXAB).
(B) Power spectral density (PSD) contrasts between baseline and omission.

## 🗺️ Narrative Context
Transitions to **FIG_06**, which quantifies these band-specific changes across the entire cortical population.
