# FIG_46: Convergent State-Space Trajectories of Predicted Events

## 🎯 Intent
To provide a unified view of how the entire cortical hierarchy represents "predicted absence" through stereotypical neural trajectories.

## 🔬 Methodology
- **Source**: `src/f046_state_space_trajectories/analysis.py`
- **Method**: PCA applied to population firing rates across all 11 areas.
- **Preprocessing**: 50ms Gaussian smoothing, Z-score normalization.
- **Visualization**: 3D Trajectory in PC-space.

## 📊 Observations
- Stereotypical paths: Neural activity for standard stimuli follows a circular, predictable path.
- Omission divergence: Upon omission, the population "derails" into a specific "error manifold" that is conserved across sessions.
- Hierarchical convergence: Trajectories in PFC show higher dimensionality and longer-lasting divergence than in V1.

## 📝 Caption & Labels
**Figure 46. Final Synthesis of Cortical State-Space Dynamics.**
(A) 3D PCA trajectories for V1 and PFC showing stimulus-driven vs. omission-driven paths.
(B) Euclidean distance between standard and omission trajectories over time.

## 🗺️ Narrative Context
Concludes the manuscript by integrating theory (FIG_01) with multi-area empirical proof.
