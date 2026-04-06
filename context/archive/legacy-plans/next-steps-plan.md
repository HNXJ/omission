# 🎯 Phase 2: Paper-Centric Omission Analysis Roadmap

Following the establishment of the **Figure-First Architecture** and the successful generation of Figures 1-4, Phase 2 focuses on finalizing the system-level population dynamics, behavioral signatures, and formally drafting the manuscript.


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

Make all these figures based on the existing codes, skills and content we alread have, but now in this folder and with that [condition]_[sequence]_[analysis] format explaned for each folder group below. Save both as .html, .svg and use PLOTLY. Use the whie baground theme. Any statistical operation (average, mean, std, var) must have statistics reported in each figure's caption, and the figure to include errorbares and a shade patch with facealpha=0.5 of the mean trace color. [all conditions] means all 12 conditions from aaab, axab, ... to rrrx. otherwise, it will be specified which ones. [full] mean from onset of fx till offset of d4, otherwise specified. analysis will be described or cued.

figures/oglo/fig_02_EYE_DVA_ALLSESSIONS/ figures : [all conditions]_[full]_[eyexy signal for the specific condition trial averaged and shown with errorbar-shades, and a transparent pink patch on the presentation of omission]

figures/oglo/fig_03_SPK_Firing_ALLSESSIONS/ figures : [all conditions]_[full]_[single unit spiking average per area]

figures/oglo/fig_04_SPK_5_group_kmeans_ALLSESSIONS/ figures : [rrrx]_[once for d2-p3-d3 and once for d3-p4-d4]_[each of the ~6000 units must be a member of one group. Around 3500 will be the group that their spiking activity is at least 10% more considering p-value more than 0.95 during p1 compared to d1]

figures/oglo/fig_05_LFP_dB_EXT_ALLSESSIONS/ figures : [all omission conditions which have X in their label]_[p2 if X is 2nd presentation (such as AXAB, BXBA, RXRR), p3 if X is 3rd, either d1-p2-d2 or d2-p3-d3]_[Time-frequency resonse plot power trace for each area, all sessions. Traces will be the same as use before, but remember errorbar as shade patch]

figures/oglo/fig_06_LFP_dB_EXT_ALLSESSIONS/ figures : [all omission conditions which have X in their label]_[p2 if X is 2nd presentation (such as AXAB, BXBA, RXRR), p3 if X is 3rd, either d1-p2-d2 or d2-p3-d3]_[Time-frequency resonse plot power trace for each area, all sessions similar to fig_05 but this time, average both conditions that omission is 2nd and omission is 3rd, one subplot for each band from theta to gamma, +-2SEM, each subplot will have 11 traces with their error bar shade patch for that band. Another subplot for the sorted order of areas based on each band power change in dB, from most positive or highest to most negative or lowest]

## 2. Manuscript Drafting (The Figure-First Protocol)
**Objective**: Build the "Source of Truth" for the Methods and Results sections.
- **Methods Draft**: Transcribe the "Methodology" sections from `docs/figures/FIG_XX.md`.
- **Results Draft**: Transcribe the "Observations" and "Captions" from the manifests.
- **Statistical Refinement**: Finalize p-values and significance markers for all 6 figures.

### 🛠️ Immediate Next Action:
**Proceed with Task 0: Behavioral Eye-Signal Classification**
