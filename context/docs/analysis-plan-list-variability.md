# Analysis Plan: Neural Variability & Precision Quenching

## 1. Mean-Matched Fano Factor (MMFF)
**Objective**: Quantify the reduction in across-trial spike count variability (quenching) during stimulus and omission windows.
- **Algorithm**: Churchland et al. (2010). Matches the distribution of firing rates across time bins to ensure variability changes are not simply a byproduct of firing rate changes.
- **Implementation**: 50ms sliding window, 10ms step. 20x subsampling repeats to identify the Greatest Common Distribution (GCD).
- **Hypothesis**: Hierarchy-dependent quenching. High-order areas (PFC) should show earlier or more pronounced quenching during omissions due to top-down predictive signaling.

## 2. Mean-Matched Variation (MMV) for Continuous Signals
**Objective**: Adapt MMFF logic for LFP and MUAe signals.
- **Algorithm**: Match Mean Absolute Value (MAV) distributions across channels or sessions.
- **Metric**: Across-trial variance of the continuous signal.
- **Correction**: Normalizing by MAV (equivalent to "Mean" in spikes) ensures that signal amplitude fluctuations don't bias the variability measure.

## 3. LFP Burst-Event Fano Factor
**Objective**: Treat oscillatory bursts as discrete events to audit the reliability of rhythmic coordination.
- **Detection**: Dual-threshold burst detection (e.g., 3x median of envelope) in Theta (3-8Hz), Alpha (8-14Hz), Beta (13-30Hz), and Gamma (35-80Hz).
- **Metric**: Fano Factor computed on "Burst Onsets" across trials.
- **Insight**: High Fano Factor = Stochastic burst timing; Low Fano Factor = Phase-locked or stimulus-timed oscillatory precision.

## 4. Post-Omission Quenching (The "Tightening" Hypothesis)
**Objective**: Determine if surprise (omission) leads to enhanced precision in subsequent presentations.
- **Contrast**: Compare MMFF/MMV of Presentation 3 in `AAAB` (Standard) vs `AXAB` (Omission at P2).
- **Prediction**: P3 in `AXAB` will show significantly lower variability than P3 in `AAAB`, reflecting a gain-increase in the internal model following a violation.

## 5. Area-Level Aggregation
- Aggregate traces across 11 areas: V1, V2, V3d, V3a, V4, MT, MST, TEO, FST, FEF, PFC.
- Map the "Quenching Latency" (time to reach 50% of max quenching) to establish a variability hierarchy.
