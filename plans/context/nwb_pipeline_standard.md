# 🧬 OMISSION 2026: NWB Analysis Pipeline Standard (V1)

This document formalizes the 12-step pipeline for the Sequential Visual Omission Task. All scripts and skills MUST adhere to these protocols.

## 1. Ingest and Standardize NWB Files
- **Anchor**: Use presentation-1 onset code (**101.0**) as the primary alignment anchor (t=0).
- **Metadata**: Extract trial metadata, stimulus identity, condition labels, timing events, photodiode, eye position, spikes, MUAe, and LFP.

## 2. Canonical Event Timeline
- **Sequence**: fixation -> p1 -> d1 -> p2/om -> d2 -> p3/om -> d3 -> p4/om -> d4 -> reward.
- **Storage**: Store events in absolute NWB time and aligned time relative to code 101.0.

## 3. Condition and Context Labeling
- **Conditions**: AAAB, AXAB, AAXB, AAAX, BBBA, BXBA, BBXA, BBBX, RRRR, RXRR, RRXR, RRRX.
- **Classes**: Stimulus identity, omission position, predictable vs unpredictable, local vs global surprise.

## 4. Preprocessing and QC
- **Rejection**: Reject broken fixation, photodiode mismatch.
- **Synchronization**: Verify V1 timing (40–60 ms post-photodiode peak).
- **Units**: Unit stability checks; separate single units from MUAe.
- **LFP**: Bipolarize/re-reference; inspect line noise.

## 5. Aligned Signal Extraction
- **Windows**: p1 onset, omission onset, post-omission stimulus onset, fixation baseline.
- **Streams**: SPK (PSTH), MUAe (Envelope), LFP (Spectral).

## 6. Core Neural Metrics
- **Spiking**: PSTH, omission/stimulus selectivity, quenching/rebound, latency.
- **MUAe**: Amplitude modulation, condition contrasts, quenching.
- **LFP**: TFR (theta, alpha, beta, gamma), coherence, Granger causality.
- **Theory**: Omission -> ↓ low-freq, ↑ beta coherence, stable gamma.

## 7. Hierarchical Separation
- **Low-Order**: V1, V2.
- **Mid-Order**: V4, MT, MST, TEO, FST.
- **High-Order**: FEF, PFC.
- **Directionality**: Test for top-down propagation (High -> Low).

## 8. Omission as Internal-Model Event
- **Contrast**: Compare omission against matched non-omission gray windows (Ghost Signal).
- **Persistence**: Quantify internal state duration during gray-screen.

## 9. Post-Omission Precision / Quenching
- **Metrics**: Fano Factor, reliability, quenching of neural dispersion.
- **Contrast**: Post-omission vs matched post-stimulus.

## 10. Band-Specific Connectivity
- **Gamma (35–70 Hz)**: Feedforward sensory drive.
- **Beta (15–25 Hz) / Alpha (8–13 Hz)**: Predictive feedback.
- **Theta (4–8 Hz)**: Coordination/state modulation.

## 11. Statistical Testing
- **LFP**: Cluster-based permutation tests.
- **Laminar**: Wilcoxon rank-sum for superficial vs deep.
- **Reporting**: Session-wise first, then group summary.

## 12. NWB Outputs / Bundles
- **Analysis Bundle**: Aligned trial table, spectral metrics, coherence matrices, summary JSON.

---
*Reference: user_pipeline_update_20260403*
