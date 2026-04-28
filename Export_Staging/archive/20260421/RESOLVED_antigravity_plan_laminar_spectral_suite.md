# RESOLVED TASK - Execution Summary
- **Agent**: `antigravity`
- **Status**: Architectural Plan drafted.
- **Key Deliverables**: 
    - Rigorous 5,416 'Stable-Plus' filtering protocol.
    - Bipolar LFP preprocessing and bootstrapped 95% CI strategy.
    - Dual-stratification logic (LaminarMapper + Spectrolaminar validation).
- **Halt**: Standing by for user review and refinement injection.

---

# Architectural Plan: Laminar Spectral Suite (f042-f043)

This plan outlines the implementation of depth-resolved spectral analyses to isolate laminar signatures of predictive feedback (Beta/Delta) and error signaling (Gamma).

## 1. Data Acquisition & Integrity
- **Engine**: Utilize `DataLoader` with `mmap_mode='r'` for optimized access to the `D:\drive\data\arrays` LFP and SPK tensors.
- **Census Enforcement**: 
    - Load unit-level metrics from `D:\drive\outputs\oglo-8figs\f041-laminar-analysis\putative_cell_metrics.csv`.
    - Apply a boolean mask to isolate the **5,416 'Stable-Plus'** units (criteria: FR > 1.0Hz, SNR > 0.8, 100% trial presence).
    - Log the final unit count per area to verify alignment with the canonical Figure 41 census.

## 2. Laminar Stratification & Mapping
- **LFP Stratification (f042)**: 
    - Group probe channels into three strata per `LaminarMapper` defaults: **Superficial (0-40)**, **L4 (40-70)**, and **Deep (70-128)**.
    - **Validation**: Cross-reference with the `analysis-spectrolaminar` skill. Compute the Alpha/Beta vs. Gamma crossover point per probe; if the crossover deviates significantly from Channel 40, adjust boundaries dynamically to maintain physiological L4 centering.
- **Unit Stratification (f043)**: 
    - Assign each 'Stable-Plus' unit to a stratum based on its `peak_channel`.
    - Maintain E/I classification from `putative_cell_metrics.csv`.

## 3. f042: Laminar Power Spectral Density (PSD)
- **Preprocessing**: 
    - Apply **Bipolar Referencing** (local channel subtraction) to localize the signal and mitigate volume conduction artifacts.
- **Spectral Estimator**: 
    - Compute **STFT** (Hanning window, 98% overlap, 1000ms windows).
    - Frequency range: 2–100 Hz.
- **Normalization**: 
    - Apply dB transformation: $10 \times \log_{10}(P / P_{base})$ using the **-250ms to -50ms** baseline window.
- **Analysis**: 
    - Compute Mean Power per stratum for Omission vs. Control trials.
    - Focus on Area V1 (Primary) and PFC (Top-level).

## 4. f043: Laminar Spike-Field Coherence (SFC)
- **Metric**: **Phase-Locking Value (PLV)** / Mean Resultant Vector (MRV).
- **Protocol**:
    - Extract LFP phases at exact spike times using Hilbert-transformed band-limited LFP.
    - **Spike-Count Equating**: Subsample spikes per stratum/condition to the global minimum spike count to prevent PLV bias.
    - Focus on the **Delta (2-4 Hz)** band, which previously showed high top-down feedback modulation.
- **Pairs**: Compute intra-area SFC (Unit and LFP from the same stratum) and inter-strata SFC (e.g., Deep Unit to Superficial LFP).

## 5. Statistical Rigor & Robustness
- **Bootstrap Protocol**: 
    - To compute **95% Confidence Intervals** robust to trial-wise outliers:
    - Perform **N=1000 bootstrap resamples** of trials within each condition.
    - Compute the mean PSD/SFC for each resample.
    - Shaded regions in plots will represent the 2.5th and 97.5th percentiles of the bootstrap distribution.
- **Artifact Rejection**: Channels with variance > 3σ from the probe mean or containing NaN segments will be deselected prior to stratification.

## 6. Visualization Standards
- **Aesthetic**: **Madelane Golden Dark** (#CFB87C / #9400D3).
- **Plot Types**: 
    - 2D Power Spectra with 95% CI shading.
    - SFC coherence spectra with Delta-band highlights.
    - Polar phase histograms for significant laminar locking.
- **Export**: Kaleido-Free interactive HTML with native SVG download capabilities enabled.
