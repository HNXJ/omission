# FIG_07: Spike-Field Coherence (SFC)

## 🎯 Intent
To determine if local spiking activity is phase-locked to the global oscillatory rhythm during the omission response.

## 🔬 Methodology
- **Source**: `src/f007_sfc/analysis.py`
- **Metric**: PPC (Pairwise Phase Consistency) to ensure bias-free estimation.
- **Window**: Omission window (1000-1500ms) vs. Pre-stimulus baseline.
- **Units**: All Stable-Plus units mapped to local LFP.

## 📊 Observations
- Phase-locking: Significant enhancement of gamma-band SFC during the omission window.
- Hierarchical gradients: Higher-tier areas show stronger phase-locking to the local oscillatory rhythm than lower-tier areas.

## 📝 Caption & Labels
**Figure 7. Oscillatory Gating of the Omission Response via Spike-Field Coherence.**
(A) Grand average SFC spectra for V1, V4, and PFC.
(B) Change in SFC (Delta-SFC) across frequency bands during omission.
(C) Polar distribution of preferred spiking phases relative to the LFP rhythm.

## 🗺️ Narrative Context
Transitions to **Phase 3 (Connectivity)**, where we investigate the directed influence between these hierarchical levels.
