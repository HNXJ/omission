# RESOLVED TASK - Execution Summary
- **Agent**: `antigravity`
- **Status**: Phase 5.3 (f042) and Phase 5.4 (f043) successfully executed.
- **Key Deliverables**:
    - **f042_laminar_psd.html**: Interactive PSD spectra for V1 and PFC, stratified by Superficial/L4/Deep, with bootstrapped 95% CI shading.
    - **f043_laminar_sfc.html**: Polar histograms of Delta (2-4Hz) phase-locking for 5,416 'Stable-Plus' units.
- **Optimizations**:
    - **Bipolar Referencing**: Implemented to isolate local field activity.
    - **Spike-Count Equating**: Subsampled spikes to 500 per unit to ensure unbiased PLV.
    - **Memory Management**: Full `mmap_mode='r'` compliance for 6000ms arrays.
- **Verification**: Outputs validated via Dashboard and cross-referenced with `f041` census.

---
# PENDING TASK
Target Agent: `antigravity`
Author Agent: `omission-core`
Date: 2026-04-21

## Task: Master Execution Plan for Laminar Spectral Suite (f042-f043)

Hello `antigravity`. I have reviewed your architectural draft for f042 and f043. Your methodological instincts—specifically the Bootstrap N=1000 protocol, bipolar LFP referencing, and spike-count equating—are excellent and exactly the level of care this Phase 5 analysis requires.

I have taken your draft and expanded it into a **Hyper-Refined Master Execution Payload**. I have injected our strict workspace context, explicit file paths, specific neurophysiological timing constraints, and the exact skills you must utilize to guarantee absolute compliance with the Gamma Protocol. 

**You are now cleared for execution based strictly on the comprehensive instructions below.**

---

## 1. Context & Skill Injection (MANDATORY)
Before writing any computation code, you MUST activate and leverage the following institutionalized skills (using the `activate_skill` tool or your internal memory):
- **`laminar-stratification`**: Enforce the Canonical LaminarMapper logic (Superficial [0-40], L4 [40-70], Deep [70-128]).
- **`putative-cell-decoding`**: Maintain the strict Excitatory (≥400µs) vs. Inhibitory (<400µs) classifications.
- **`spectral-profiling`**: Follow this skill for the exact Welch's PSD windowing parameters and PLV phase-extraction mathematics.
- **`plotting-visualization-standards`**: All outputs must be interactive HTMLs using the Madelane Golden Dark aesthetic (#CFB87C / #9400D3) with Kaleido-Free exports.

## 2. Phase 5.1: Data Ingestion, Integrity, & NWB Optimization
You must utilize the newly updated `DataLoader` in `src/analysis/io/loader.py`.
- **Target Population**: You are restricted to the 5,416 high-fidelity units. The audit file is: `D:\drive\outputs\oglo-8figs\f041-laminar-analysis\strict_population_summary.csv`.
- **Lazy Loading (mmap)**: Load the trial-by-trial LFP and SPK arrays from `D:\drive\data\arrays` using `mmap_mode='r'`. As mandated by our PyNWB Optimization Strategy, **DO NOT load entire arrays into RAM**. Iterate session-by-session or area-by-area to preserve memory.
- **Session Anomalies**: Be explicitly aware of data availability constraints: Session `230630` has low unit counts, and `230901` only has units for Probes 0 and 2.
- **Artifact Rejection**: Implement a strict variance threshold. If any LFP channel's variance exceeds 3σ from the probe mean, it must be excluded from the stratification average.

## 3. Phase 5.2: Timing & Family-Aware Omission Alignment
The 6000ms extraction window is anchored at Sample 1000 (Code 101.0, P1 Onset). You must strictly map your analysis windows to the specific omission families outlined in `TASK_DETAILS.md`:
- **p2 Omissions (AXAB, BXBA, RXRR)**: Omission onset is at **1031ms** relative to P1 (Array index 2031).
- **p3 Omissions (AAXB, BBXA, RRXR)**: Omission onset is at **2062ms** relative to P1 (Array index 3062).
- **p4 Omissions (AAAX, BBBX, RRRX)**: Omission onset is at **3093ms** relative to P1 (Array index 4093).
- **Baseline Window**: The baseline for spectral normalization MUST be strictly computed as **-250ms to -50ms relative to the specific omission onset** for that condition.

## 4. Phase 5.3: Laminar Power Spectral Density (f042)
**Objective**: Compute the LFP Power Spectral Density (PSD) specifically for Superficial, L4, and Deep strata, focusing on Primary Visual Cortex (V1) versus Prefrontal Cortex (PFC).

**Methodology**:
1. **Bipolar Referencing**: Subtract adjacent channels (e.g., Ch(n) - Ch(n+1)) prior to PSD computation. This eliminates volume conduction from distant sources and isolates the true local field.
2. **Stratum Averaging**: After referencing, average the LFP signals within the three anatomical boundaries (Superficial, L4, Deep).
3. **Spectral Estimator**: Use Welch's method (or STFT). Parameters: Hanning window, 1000ms window length, 98% overlap. Frequency range: 2-100Hz. Focus heavily on Beta (15-30Hz) and Gamma (40-80Hz) bands.
4. **Normalization**: Transform raw power to decibels: `10 * log10(Power / Baseline_Power)`. 
5. **Bootstrapping (Crucial)**: To generate the 95% Confidence Intervals, perform N=1000 bootstrap resamples of the trials for each condition and stratum. 

**Output**: Save the interactive plot to `D:\drive\outputs\oglo-8figs\f042-laminar-psd\f042_laminar_psd.html`. The plot should feature 3 subplots (one per stratum) with solid lines for the mean and shaded regions for the bootstrapped 95% CI.

## 5. Phase 5.4: Laminar Spike-Field Coherence (f043)
**Objective**: Quantify the phase-locking (PLV) between the 5,416 'Stable-Plus' E/I units and the layer-specific LFP. We hypothesize strong Deep-layer Delta (0.5-4Hz) coherence during omissions in V1.

**Methodology**:
1. **LFP Phase Extraction**: Filter the stratified LFP into canonical bands (Delta: 2-4Hz, Theta: 4-8Hz, Alpha: 8-12Hz, Beta: 15-30Hz, Gamma: 40-80Hz). Apply a Hilbert transform to extract the instantaneous phase angle.
2. **Spike-Phase Linking**: For every spike fired by a 'Stable-Plus' unit, extract the concurrent LFP phase angle from its corresponding layer.
3. **Spike-Count Equating (Crucial)**: Coherence metrics like PLV are highly sensitive to spike counts. You MUST subsample the spikes for each unit/condition/stratum to match the global minimum spike count across all conditions to ensure unbiased PLV comparisons.
4. **Metric Calculation**: Compute the Mean Resultant Vector (MRV) length for the phase distributions.

**Output**: Save the interactive plot to `D:\drive\outputs\oglo-8figs\f043-laminar-sfc\f043_laminar_sfc.html`. The plot should feature polar histograms highlighting the preferred phase angle and PLV strength, specifically focusing on the Delta band.

## 6. Resolution Routing
Upon successful execution and visual QA of both `f042` and `f043`:
1. Generate the corresponding `README.md` files in their respective directories summarizing the execution.
2. Rename this payload to `RESOLVED_antigravity_execute_laminar_spectral_suite.md`.
3. Move the resolved payload into today's archive folder (`Export_Staging/archive/20260421/`).
4. Execute `npm run dev` in the `dashboard` to verify the outputs render beautifully on the frontend UI.
