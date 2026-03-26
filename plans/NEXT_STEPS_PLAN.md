# 🎯 Phase 2: Paper-Centric Omission Analysis Roadmap

Following the establishment of the **Figure-First Architecture** and the successful generation of Figures 1-4, Phase 2 focuses on finalizing the system-level population dynamics, behavioral signatures, and formally drafting the manuscript.

## 0. Behavioral Eye-Signal Classification (TOP PRIORITY)
**Objective**: Decode task context (Identity, Order, Omission Identity, Block, Condition) using oculomotor signals.
- **Data**: Extract X/Y DVA-calibrated eye position and Pupil diameter from `.mat` files.
- **Analysis**: Identify and classify directions of eye-movements and microsaccades.
- **Visualization**: Generate Rose Plots (Polar Histograms) of directions for each task context.
- **Storage**: Figures in `/figures/`, Scripts in `/scripts/`, Functions in `/functions/`.

## 1. Figure 5: Population Dynamics & Manifold Divergence
**Objective**: Visualize and quantify the "Neural Surprise" state-space trajectory.
- **3D Trajectories**: Use PCA/UMAP to project population activity for **Standard (RRRR)** vs. **Omission (AAAX)**.
- **Divergence Distance**: Compute the millisecond-by-millisecond Euclidean distance in the PC-space.
- **Surprise Latency**: Identify the exact time point when the state deviates from the "Expected" trajectory across the 11-area hierarchy.

## 2. Figure 6: Directionality & Spectral Coordination (V1 vs. PFC)
**Objective**: Formally test if V1 "drives" the PFC omission signal or if they are coordinated via feedback.
- **Lag Analysis**: Compute spike-spike cross-correlograms between V1 and PFC omission neurons.
- **Granger Causality (LFP)**: Use frequency-dependent causality to dissociate **Feedforward (Gamma)** from **Feedback (Beta/Alpha)**.

## 3. Manuscript Drafting (The Figure-First Protocol)
**Objective**: Build the "Source of Truth" for the Methods and Results sections.
- **Methods Draft**: Transcribe the "Methodology" sections from `docs/figures/FIG_XX.md`.
- **Results Draft**: Transcribe the "Observations" and "Captions" from the manifests.
- **Statistical Refinement**: Finalize p-values and significance markers for all 6 figures.

## 4. Remote Office Mac Deployment (Qwen 3.5 MLX)
**Objective**: Finalize automated login and launch the LLM server for advanced reasoning tasks.
- **Automated Login**: Complete the SSH handshake with `10.32.133.50`.
- **Qwen3.5-35B-A3B-8bit**: Launch the MLX model for deep architectural and neuroscience-heavy reasoning.

---
### 🛠️ Immediate Next Action:
**Proceed with Task 0: Behavioral Eye-Signal Classification?**
