# Phase D: High-Dimensional State-Space Trajectory Analysis (f046)
**Date**: 2026-04-24
**Target**: Omission Analytical Core (CLI)
**Status**: INITIATED (User Approved)

## 1. Objective
To visualize the population dynamics of 'Stable-Plus' neurons as they traverse the cortical manifold during the omission window. We aim to identify rhythmic rotational dynamics (jPCA) or distinct state-space clusters that differentiate "Stimulus Expectation" from "Prediction Error."

## 2. Methodology & Implementation Plan

### 2.1 Dimensionality Reduction (f046)
- **Algorithm**: Principal Component Analysis (PCA) followed by jPCA (Churchland et al. 2012) to extract rotational components.
- **Data Input**: Trial-averaged PSTHs (smoothed 20ms) for all 'Stable-Plus' units within an area.
- **Temporal Window**: Strict `[-500, +1000]ms` relative to Omission Onset to capture the pre-omission ramp and post-omission decay.

### 2.2 Critical Comparisons
- **Hierarchical Divergence**: Contrast the trajectory of V1 (Low) vs. PFC (High). We expect PFC to exhibit more complex, anticipatory rotational dynamics.
- **Surprise Scaling**: Plot AXAB (Expected) vs. AXBB (Rare/Surprise) trajectories in the same state-space to measure manifold distance.

## 3. Visualization Mandates
- **3D Trajectories**: Use Plotly `go.Scatter3d` to show PC1, PC2, and PC3.
- **Time Animation**: Use `frames` to animate the trajectory progression over time.
- **Aesthetic**: Madelane Golden Dark palette. Trace color should transition from **Gold** (pre-omission) to **Violet** (post-omission).
- **Export**: Synchronized SVG and HTML.

## 4. Next Steps for CLI Core
1. **Develop `src/f046_state_space/analysis.py`**: Implement PCA and trajectory extraction.
2. **Develop `src/f046_state_space/plot.py`**: Create the 3D animated trajectories.
3. **Execute across all 11 areas**.
4. **Sync**: Run `npm run sync` to update the dashboard.

**Proceed with Phase D initialization.**
