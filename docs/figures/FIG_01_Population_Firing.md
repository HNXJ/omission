# Figure 1: Population Firing Rates across 11 Cortical Areas

## 🎯 Intent
To provide a brain-wide overview of neural activity during the Visual Omission Oddball paradigm and determine if population-level averages can distinguish between standard and omission conditions.

## 🔬 Methodology
- **Data Source**: 13 NWB sessions, 6,040 mapped neurons.
- **Mapping**: Robust 128-channel/probe logic; DP mapped to V4; V3 split into V3d/V3a.
- **Signal**: Single-unit average firing rates (Hz).
- **Processing**:
    - Gaussian Smoothing (100ms window, 20ms SD).
    - Mean and SEM calculated across all units per area.
- **Conditions**: RRRR (Brown), RXRR (Red), RRXR (Blue), RRRX (Green).
- **Visualization**: Plotly line charts with ±SEM patch-shades. Window: -750ms to 4124ms.

## 📊 Observations
- Stimulus onset (p1, p2, p3) triggers robust and significant firing rate increases across all visual areas (V1-V4, MT).
- During the omission window (e.g., p4 of RRRX), the population-level average is highly overlapping with the standard condition (RRRR), indicating that the omission response is either subtle or carried by a specific subset of neurons not dominant in the grand average.
- Clear latency hierarchy observed from V1 towards PFC.

## 📝 Caption & Labels
**Figure 1. Population-level dynamics during visual omission.** Average firing rates (Hz) for 11 cortical areas across four conditions: Standard (RRRR, brown), Omit p2 (RXRR, red), Omit p3 (RRXR, blue), and Omit p4 (RRRX, green). Shaded regions indicate ±SEM across units. Data files: `FIG_01_Population_Firing_[Area].html/svg`.

## 🗺️ Narrative Context
Figure 1 shows that grand averages mask the omission response, leading us to Figure 2, which investigates the functional diversity of single neurons.
