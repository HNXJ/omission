# Methods: Phase 2 - Spectral Analysis

## 🔬 Time-Frequency Representation (TFR)
Broadband spectral power was estimated using the multitaper method (7 Slepian tapers, time-bandwidth product = 4). LFP signals were segmented into trials of 4000ms duration, aligned to the omission onset (P2 position). Power was calculated for frequencies between 4 and 100Hz in steps of 2Hz.

## 🔬 Baseline Normalization (dB)
To account for 1/f power law distribution, raw power values were baseline-normalized into decibels ($dB$) using the formula:
$$P_{norm}(f, t) = 10 \times \log_{10} \left( \frac{P(f, t)}{\bar{P}_{base}(f)} \right)$$
The baseline period ($\bar{P}_{base}$) was defined as the pre-stimulus interval from -1000 to -500ms relative to the first stimulus (P1) onset.

## 🔬 Spike-Field Coherence (SFC)
The coordination between single-unit spiking and local field potential (LFP) oscillations was quantified using Pairwise Phase Consistency (PPC). PPC provides an unbiased estimate of phase-locking strength that is independent of the number of spikes or trials. SFC was calculated separately for the following canonical bands:
- **Theta**: 4-8Hz
- **Alpha**: 8-13Hz
- **Beta**: 15-25Hz
- **Gamma**: 40-80Hz
Significant increases in SFC during the omission window (1000-1500ms) were identified using a Wilcoxon Signed-Rank test against the pre-stimulus baseline.
