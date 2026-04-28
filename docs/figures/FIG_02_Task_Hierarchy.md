# FIG_02: Task Architecture & Cortical Hierarchy

## 🎯 Intent
To define the physical and temporal constraints of the experiment, mapping the 11-area V1-PFC axis and the rhythmic stimulus sequence.

## 🔬 Methodology
- **Source**: `src/f002_psth/plot.py`
- **Recording**: 128-channel linear probes across V1, V2, V3, V4, MT, MST, TEO, FST, FEF, and PFC.
- **Task**: AXAB, BXBA, RXRR sequences.
- **Timing**: Stimuli at 500ms intervals (2Hz rhythm). Omissions occur stochastically at the P2 position.

## 📊 Observations
- Hierarchical mapping: Reliable latency gradients from V1 (~40ms) to PFC (~100ms).
- Stable populations: Identification of 842 "Stable-Plus" units across all sessions.

## 📝 Caption & Labels
**Figure 2. Spatiotemporal Mapping of the Cortical Hierarchy.**
(A) Topography of linear probe insertions across the macaque visual and prefrontal cortex.
(B) Task timeline: Rhythmic stimulus blocks with stochastic omissions.
(C) Population stability across sessions (GPA-verified).

## 🗺️ Narrative Context
Sets the stage for **FIG_03**, the population-level response to the omission event.
