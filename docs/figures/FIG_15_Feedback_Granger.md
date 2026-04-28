# FIG_15: Top-Down Routing of Internal Predictions (Granger FB)

## 🎯 Intent
To demonstrate that internal predictions are carried by feedback-dominant alpha/beta rhythms from deep layers of higher-tier areas.

## 🔬 Methodology
- **Source**: `src/f015_spectral_granger/analysis.py`
- **Method**: Non-parametric Spectral Granger Causality.
- **Direction**: PFC_Deep -> V1_Sup.
- **Frequencies**: 8-25Hz (Alpha/Beta).

## 📊 Observations
- Feedback dominance: Strong alpha/beta Granger influence from PFC to V1 prior to and during the omission.
- Predictive routing: Internal models modulate lower-tier activity to anticipate upcoming sensory events.

## 📝 Caption & Labels
**Figure 15. Feedback Control of Sensory Predictions.**
(A) Spectral Granger influence (PFC -> V1) peaking in the Beta band.
(B) Dynamic shift in feedback strength as a function of sequence predictability.

## 🗺️ Narrative Context
Leads to **Phase 4 (Behavior & Decoding)**, where we test if these neural signals can predict the animal's behavior and internal state.
