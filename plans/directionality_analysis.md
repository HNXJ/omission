# Plan: V1 vs. PFC Directionality Analysis

## 🎯 Objective
Characterize the causal interaction between V1 and PFC during visual omission windows using cross-correlation and Granger Causality.

## 🔬 Hypothesis
- **Feed-forward (V1 -> PFC)**: Dominant in the **Gamma band** (35-70Hz) as a prediction error signal.
- **Feedback (PFC -> V1)**: Dominant in the **Beta band** (13-30Hz) as a top-down predictive signal.

## 🛠️ Implementation Steps

### Phase 1: Data Extraction & Unit Identification
1. **Target Sessions**: 230630, 230816, 230830 (Simultaneous V1 + PFC).
2. **Identification**:
   - Locate V1 and PFC units in these sessions using NWB metadata.
   - Filter for "Real" omission units: Firing rate in the omission window (4093-4624ms) must peak and exceed all preceding stimulus/fixation intervals.
3. **Data Loading**:
   - Extract LFP from V1 and PFC probes.
   - Extract Spikes for identified omission units.

### Phase 2: Spike-Spike Connectivity
1. **Cross-Correlation**: Compute CCGs between V1 and PFC omission units.
2. **Lag Analysis**: Identify the peak lag (V1-leads-PFC vs PFC-leads-V1).

### Phase 3: LFP-LFP Granger Causality
1. **Framework**: Use `nitime` for spectral Granger Causality analysis.
2. **Window**: Analyze the 4093-4624ms window (P4 Omission).
3. **Bands**: Compare GC(V1->PFC) and GC(PFC->V1) across Beta (13-30Hz) and Gamma (35-70Hz).

### Phase 4: Visualization
1. **Causality Plots**: Plot Spectral GC vs Frequency for both directions.
2. **Coherence**: Plot LFP-LFP coherence as a baseline connectivity measure.
3. **Save Results**: Store figures in `/figures/connectivity/`.

## ✅ Verification
- Confirm if Gamma GC is significantly higher for V1 -> PFC.
- Confirm if Beta GC is significantly higher for PFC -> V1.
