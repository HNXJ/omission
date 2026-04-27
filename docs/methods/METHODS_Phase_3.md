# Methods: Phase 3 - Connectivity & Granger Causality

## 🔬 Multivariate Spiking Granger Causality
To quantify the directed information flow between cortical areas at the level of spiking activity, we employed multivariate Granger Causality (GC) analysis. 
1. **Source/Target Definition**: We segmented the cortical column into Superficial (channels < 64) and Deep (channels >= 64) layers.
2. **Signal Aggregation**: Spike trains for all units in a given area-layer segment were aggregated into population rate signals (1ms bins).
3. **Stationarity**: First-order differencing was applied to ensure the time-series were stationary.
4. **MVAR Modeling**: A multivariate autoregressive (MVAR) model was fitted to the source and target signals using the Akaike Information Criterion (AIC) to determine optimal lag (up to 20ms).
5. **F-Statistic**: The Granger F-statistic was used as the metric for directed influence.

## 🔬 Non-parametric Spectral Granger Causality
For frequency-resolved directed influence, we calculated spectral Granger causality using the non-parametric factorization of the cross-spectral density matrix. This allowed us to distinguish between feedforward-dominant gamma flow and feedback-dominant alpha/beta flow.

## 🔬 Phase-Amplitude Coupling (PAC)
Cross-frequency coupling was assessed using the Modulation Index (MI). We quantified the coupling between the phase of low-frequency oscillations (4-25Hz) and the amplitude of high-frequency gamma oscillations (40-100Hz) during the omission window.
