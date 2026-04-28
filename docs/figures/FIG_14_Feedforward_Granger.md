# FIG_14: Hierarchical Flow of Prediction Errors (Granger FF)

## 🎯 Intent
To prove that omissions trigger a feedforward-dominant signal flow from superficial layers of lower-tier areas to deeper layers of higher-tier areas.

## 🔬 Methodology
- **Source**: `src/f014_spiking_granger/analysis.py`
- **Method**: Multivariate Spiking Granger Causality.
- **Direction**: Superficial (Source) -> Deep (Target).
- **Time Window**: Omission window (1000-1500ms).
- **Lags**: MVAR model with 20ms history.

## 📊 Observations
- Feedforward dominance: Significant increase in V1_Sup -> PFC_Deep Granger influence during the omission.
- Information routing: Prediction errors are prioritized in the feedforward channel when sensory input is missing.

## 📝 Caption & Labels
**Figure 14. Feedforward Propagation of Neural Prediction Errors.**
(A) Directed information flow (Granger F-statistic) from V1 Superficial to PFC Deep layers.
(B) Contrast of FF vs. FB flow during standard vs. omission trials.

## 🗺️ Narrative Context
Complements **FIG_15**, which examines the feedback channel carry internal predictions.
