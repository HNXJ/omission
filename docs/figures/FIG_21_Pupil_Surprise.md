# FIG_21: Physiological Readouts of Sensory Surprise (Pupil)

## 🎯 Intent
To correlate neural omission responses with autonomic arousal, proving that omissions are perceived as meaningful behavioral events.

## 🔬 Methodology
- **Source**: `src/f021_pupil_decoding/analysis.py`
- **Recording**: Eye-tracking (0.1ms resolution) synchronized via BHV2.
- **Metric**: Pupil Diameter (Z-scored) and Blink Rate.
- **Alignment**: Aligned to omission onset.

## 📊 Observations
- Autonomic surge: Significant increase in pupil diameter following the omission (~500-1000ms latency).
- Surprise correlation: Pupil dilation scales with the strength of the neural prediction error in PFC.

## 📝 Caption & Labels
**Figure 21. Behavioral and Autonomic Signatures of Sensory Omission.**
(A) Average pupil diameter time-course for standard vs. omission trials.
(B) Correlation between PFC gamma-burst magnitude and peak pupil dilation.

## 🗺️ Narrative Context
Provides the behavioral grounding for the neural dynamics explored in the previous phases.
