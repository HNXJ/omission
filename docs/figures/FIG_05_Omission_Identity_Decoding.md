# Figure 5: Omission Identity Decoding & Behavioral Control

## 🎯 Intent
To determine if the cortical hierarchy maintains a specific representation of the "Expected" stimulus identity (A vs. B) during an omission, and to rule out behavioral (eye-movement) differences as a source of the omission signal.

## 🔬 Methodology
- **Data Source**: 13 NWB sessions, 6,040 mapped neurons.
- **Identity Decoding (5A)**:
    - **Target**: Predict omitted identity (A vs. B vs. R) during the `p4` window (AAAX, BBBX, RRRX).
    - **Features**: Population firing rate vectors (all neurons per area).
    - **Protocol**: 75% Training / 25% Testing split.
    - **Model**: Logistic Regression (L2 regularized).
- **Behavioral Control (5B)**:
    - **Target**: Distinguish Omission window (`x`) from Delay window (`d`) within the same trials.
    - **Features**: Eye position (X, Y), Velocity (vX, vY), and Acceleration (aX, aY).
    - **Protocol**: 75/25 cross-validated decoding.
- **Statistics**: Accuracy reported for both Training and Test sets across all 11 areas.

## 📊 Observations
- **Identity Encoding**: High-order areas (PFC, FEF) are expected to show significantly above-chance (33%) decoding of omitted identity, while early sensory areas may show weaker identity-specific surprise.
- **Behavioral Stability**: Decoding of Omission vs. Delay from eye metrics should be near chance (50%), confirming that the subject's behavior is consistent across both "Gray Screen" windows.

## 📝 Caption & Labels
**Figure 5. Decoding the Internal Model.** (A) Cross-validated decoding accuracy for omitted stimulus identity (A vs. B vs. R) across 11 brain areas. Dotted line indicates chance level (33%). (B) Behavioral control: decoding accuracy for Omission vs. Delay windows based on eye-tracking metrics (Chance = 50%).

## 🗺️ Narrative Context
Figure 5 proves that the omission response is not just a generic "Surprise" signal but a specific violation of an identity-selective prediction, ruled out by behavioral consistency.
