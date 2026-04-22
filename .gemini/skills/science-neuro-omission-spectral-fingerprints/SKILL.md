---
name: science-neuro-omission-spectral-fingerprints
description: Spectral analysis framework for dissociating feedforward (Gamma) and feedback (Beta/Alpha) channels during omissions.
---
# skill: science-neuro-omission-spectral-fingerprints

## When to Use
Use this skill when analyzing LFP oscillations or performing time-frequency decompositions. It is mandatory for:
- Dissociating feedforward sensory input (Gamma $>40$Hz) from top-down predictions (Beta $15$-$30$Hz).
- Detecting "Gamma Quenching" during omission windows.
- Quantifying the "Surprise Beta" transient in PFC/FEF.
- Implementing cross-frequency coupling (CFC) analysis (e.g., Theta-Gamma).
- Mapping spectral power onto laminar CSD sinks (f042-f043).

## What is Input
- **Raw LFP**: Condition-aligned voltage traces (typically 1kHz sampling).
- **Time-Frequency Maps**: Spectrograms or Scalograms (Morlet wavelets).
- **Laminar Depth**: Channel indices mapped to Granular vs. Infragranular layers.

## What is Output
- **Power Spectra**: Average power per frequency band (Alpha, Beta, Gamma).
- **Spectrogram Contrasts**: Omission - Standard power differences in frequency-time space.
- **Directional Metrics**: Granger Causality or Phase-Slope Index in specific bands.

## Algorithm / Methodology
1. **Wavelet Transformation**: Compute the time-frequency representation using a bank of Morlet wavelets (typically 2-100Hz).
2. **Baseline Normalization**: Use $dB$ change or $Z$-score relative to the pre-stimulus period.
3. **Band Extraction**:
   - **Gamma (40-80Hz)**: Tracks bottom-up sensory drive; should vanish during omissions.
   - **Beta (15-30Hz)**: Tracks top-down priors; should surge in PFC during surprise.
   - **Alpha (8-12Hz)**: Reflects inhibition or gain modulation.
4. **Coherence Analysis**: Test for inter-areal phase synchronization in the Beta band during the omission window.

## Placeholder Example
```python
import numpy as np
from scipy.signal import spectrogram

def extract_band_power(lfp, fs=1000):
    """
    Computes spectral power in Beta and Gamma bands.
    """
    f, t, Sxx = spectrogram(lfp, fs)
    gamma = np.mean(Sxx[(f >= 40) & (f <= 80), :], axis=0)
    beta = np.mean(Sxx[(f >= 15) & (f <= 30), :], axis=0)
    return beta, gamma

# Example: Detecting Gamma quenching in V1
beta_pow, gamma_pow = extract_band_power(v1_lfp_omit)
```

## Relevant Context / Files
- [predictive-routing](file:///D:/drive/omission/.gemini/skills/predictive-routing/skill.md) — For the JAX-vectorized spectral engine details.
- [src/spectral/wavelet_transform.py](file:///D:/drive/omission/src/spectral/wavelet_transform.py) — The canonical decomposition script.
