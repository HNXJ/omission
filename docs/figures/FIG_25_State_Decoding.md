# FIG_25: State-Space Decoding of Omission Responses

## 🎯 Intent
To determine if the neural state during an omission can be decoded with high accuracy, suggesting that the omission is a distinct, reproducible cortical state.

## 🔬 Methodology
- **Source**: `src/f025_state_decoding/analysis.py`
- **Method**: Support Vector Machine (SVM) classifier with linear kernel.
- **Features**: Population activity (Z-scored FR) of 842 Stable-Plus units.
- **Cross-validation**: 10-fold cross-validation, stratified by trial type.

## 📊 Observations
- High Accuracy: Omission states can be decoded from standard stimuli with >90% accuracy in high-order areas (PFC/FEF).
- Latency: Decoding accuracy peaks ~100-200ms following omission onset, aligning with the "ghost signal" timing.
- Generalization: Decoders trained on one session show robust performance on held-out sessions, confirming a stable manifold.

## 📝 Caption & Labels
**Figure 25. High-Dimensional Decoding of Predicted Sensory Absence.**
(A) SVM classification accuracy over time, aligned to omission onset.
(B) Confusion matrix demonstrating high separability between standard and omission states.

## 🗺️ Narrative Context
Leads to **FIG_26**, the temporal evolution of this classification accuracy across the hierarchy.
