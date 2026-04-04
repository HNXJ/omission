# Analysis Plan: Multi-Scale Coordination & Connectivity

## 1. Pairwise Phase Consistency (PPC)
**Objective**: Quantify the strength of spike-LFP synchronization without bias from spike counts or trial numbers.
- **Algorithm**: Vinck et al. (2010). Unbiased measure of phase locking.
- **Implementation**: 250ms window, 50ms step. Computed for individual neuron categories (Omit-Pref, Stim-Selective, etc.) relative to local and distant LFP channels.
- **Bands**: Theta (3-8Hz), Alpha (8-14Hz), Beta (13-30Hz), Gamma (35-80Hz).
- **Hypothesis**: Omission-preferring neurons in V1 and PFC will show selective phase locking to Gamma-band rhythms during the omission window.

## 2. Inter-Regional Coherence & Phase-Lag Index (PLI)
**Objective**: Map the oscillatory synchronization between cortical hubs.
- **Metric**: Magnitude-squared Coherence and PLI (to eliminate volume conduction).
- **Network**: 11x11 area adjacency matrix (55 unique pairs).
- **Contrast**: Omission vs. Baseline (Pre-stim) and Omission vs. Stimulation.
- **Significance**: Identifies the functional networks recruited by the "Visual Void."

## 3. Cross-Correlation Histograms (CCG) & Lag Analysis
**Objective**: Resolve the temporal ordering of spikes between area pairs (e.g., V1-PFC).
- **Metric**: Lag-centered CCG with jitter correction.
- **Directionality**: Positive lag (V1 $\to$ PFC) = Feedforward; Negative lag (PFC $\to$ V1) = Feedback.
- **Application**: Focus on Omission-Preferring units to see which area triggers the "Surprise" response first.

## 4. Phase-Amplitude Coupling (PAC)
**Objective**: Audit the cross-frequency coordination within and between areas.
- **Metric**: Modulation Index (MI) (Tort et al., 2010).
- **Target**: Theta phase modulating Gamma amplitude (the "Syntactic" model of information packaging).
- **Expected Result**: Surge in Theta-Gamma coupling in PFC during omissions as it orchestrates top-down predictions.

## 5. Spectral Granger Causality
**Objective**: Quantify directional information flow in frequency space.
- **Metric**: Non-parametric Granger Causality (using `nitime` or `mvgc`).
- **Focus**: Distinguishing Gamma (FF) dominance from Beta (FB) dominance in V1-PFC interactions during violations of expectation.
