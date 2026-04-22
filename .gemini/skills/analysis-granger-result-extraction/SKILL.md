---
name: analysis-granger-result-extraction
description: Extracts and analyzes spectral Granger causality results between V1 and PFC LFP signals within defined frequency bands (e.g., Beta, Gamma) and reports the dominant direction of causality. This skill is critical for understanding directed functional connectivity between these regions during specific time windows.
---
# skill: analysis-granger-result-extraction

## When to Use
Use this skill when you need to quantify directed information flow between two brain regions across different frequency bands. It is specifically tailored for:
- Evaluating Feedforward (V1->PFC) vs. Feedback (PFC->V1) signaling.
- Comparing connectivity strength in Beta (13-30Hz) vs. Gamma (35-80Hz) bands.
- Extracting summary statistics for the Omission period (Predictive Routing hypothesis).

## What is Input
- **LFP Data**: Regional representative LFP signals (usually `.npy` format).
- **Time Window**: `tuple` - The interval of interest (e.g., `(4000, 4600)` ms).
- **Frequency Bands**: `dict` - Definitions of bands (e.g., `{'beta': (13, 30), 'gamma': (35, 70)}`).
- **Model Parameters**: `ORDER` (e.g., 15) and `SAMPLING_RATE` (e.g., 1000).

## What is Output
- **Mean Causality**: Average Granger value per band per direction.
- **Dominant Direction**: Classification of information flow (FF vs. FB).

## Algorithm / Methodology
1. **Windowing**: Slices the trial-averaged regional LFP to the specific analysis window (e.g., the Omission window).
2. **Spectral Analysis**: Computes frequency-resolved Granger causality using a Multi-Variate Autoregressive (MVAR) model.
3. **Band Averaging**: Integrates the spectral causality values across the frequencies within each defined band.
4. **Comparative Logic**: Performs a 1-to-1 comparison of the integrated values for each direction to determine the dominant signaling regime.

## Placeholder Example
```python
import numpy as np
import nitime.analysis as na
import nitime.timeseries as ts

# 1. Setup analyzer
BANDS = {'beta': (13, 30), 'gamma': (35, 70)}
analyzer = na.GrangerAnalyzer(tseries, order=15)
freqs = analyzer.frequencies

# 2. Extract values for Beta band
mask = (freqs >= 13) & (freqs <= 30)
mean_ff = np.nanmean(analyzer.causality_xy[1, 0, mask])
mean_fb = np.nanmean(analyzer.causality_yx[0, 1, mask])

print(f"Beta Connectivity: FF={mean_ff:.4f}, FB={mean_fb:.4f}")
```

## Relevant Context / Files
- [extract_granger_results.py](file:///D:/drive/omission/codes/scripts/extract_granger_results.py) — Source implementation.
- [analysis-spectrolaminar](file:///D:/drive/omission/.gemini/skills/analysis-spectrolaminar/skill.md) — For regional definition.