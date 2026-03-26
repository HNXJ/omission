# Figure 6: V1-PFC Directionality & Spectral Coordination

## 🎯 Intent
Establish the functional hierarchy and direction of information flow between early sensory (V1) and high-order executive (PFC) areas during omission. This figure tests the core prediction of hierarchical Active Inference: that surprise signals propagate bottom-up while predictions are maintained top-down.

## 🔬 Methodology
- **Data Source**: Sessions with simultaneous V1 and PFC recordings.
- **Spike-Spike Lag (6A)**:
    - **Target**: Neurons labeled as "Omit-Specific" in V1 and PFC.
    - **Calculation**: Cross-correlation histograms (CCG) with a +/- 250ms window during the `p4` omission.
    - **Metric**: Time-to-peak lag (ms).
- **LFP Granger Causality (6B)**:
    - **Target**: LFP traces from representative V1 and PFC channels.
    - **Method**: Frequency-domain multivariate Granger Causality (0-100Hz).
    - **Comparison**: Standard vs. Omission.
- **Phase-Lag Index (6C)**:
    - **Metric**: Quantifies consistent phase-locking across areas, ruling out volume conduction.

## 📊 Observations
- **V1 Leads PFC (Spikes)**: The spike-spike CCG is expected to show a positive peak (e.g., +15-30ms), indicating that V1 omission neurons fire before PFC omission neurons.
- **Feedforward Gamma (LFP)**: Granger Causality should reveal a strong V1 $\rightarrow$ PFC influence in the Gamma band (40-80Hz), consistent with error signaling.
- **Feedback Beta (LFP)**: PFC $\rightarrow$ V1 influence is expected in the Beta band (15-30Hz), representing the top-down maintenance of the internal model.

## 📝 Caption & Labels
**Figure 6. Hierarchical Coordination during Omission.** (A) Cross-correlogram (CCG) between V1 and PFC Omit-labeled units. Peak lag indicates V1 leads PFC by ~X ms. (B) Spectral Granger Causality showing Feedforward (V1 $\rightarrow$ PFC, red) and Feedback (PFC $\rightarrow$ V1, blue) influences.

## 🗺️ Narrative Context
Figure 6 provides the final "Proof of Hierarchy," confirming that while omissions are processed brain-wide (Figures 1-4), they follow a specific V1-to-PFC communication protocol consistent with Predictive Coding.
