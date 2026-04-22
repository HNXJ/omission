---
name: analysis-neuro-omission-effective-connectivity
description: Evaluates the directed influence between V1 and PFC during standard and omission trials. Focuses on the reversal of information flow (Feedforward vs. Feedback).
---
# skill: analysis-neuro-omission-effective-connectivity

## When to Use
Use this skill to determine the directionality of signaling between brain regions. It is the primary tool for:
- Testing the Predictive Routing hypothesis (PFC -> V1 during omissions).
- Comparing directed influence in Gamma (FF) vs. Beta (FB) bands.
- Quantifying the magnitude of top-down prediction error signals.

## What is Input
- **Time Series Data**: Synchronized LFP or firing rate traces from two regions.
- **Model Parameters**: `max_lag` for Autoregressive (AR) models, frequency resolution for spectral GC.
- **Windowing**: Specific epochs (Standard stimulus vs. Omission window).

## What is Output
- **GC Spectra**: Frequency-resolved directed influence for both directions ($V1 \rightarrow PFC$ and $PFC \rightarrow V1$).
- **P-Values**: Statistical significance of the directed influence.
- **Figures**: Directionality indices or "net flow" plots.

## Algorithm / Methodology
1. **MVAR Modeling**: Fits a Multi-Variate Autoregressive model to the regional signals.
2. **Spectral Decomposition**: Transforms the model coefficients into the frequency domain using the Wilson or Geweke method.
3. **Connectivity Extraction**: Calculates the transfer function and noise covariance to derive directed coherence or causality.
4. **Directionality Index**: Computes $DI = \frac{GC_{FF} - GC_{FB}}{GC_{FF} + GC_{FB}}$ to summarize the dominant flow.

## Placeholder Example
```python
from nitime.analysis import GrangerAnalyzer
from nitime.timeseries import TimeSeries

# 1. Prepare data (Regions: V1, PFC)
data = np.vstack([v1_signal, pfc_signal])
t_series = TimeSeries(data, sampling_rate=1000)

# 2. Compute Spectral GC
analyzer = GrangerAnalyzer(t_series, order=15)
freqs = analyzer.frequencies
gc_v1_to_pfc = analyzer.causality_xy[1, 0]
gc_pfc_to_v1 = analyzer.causality_yx[0, 1]

print(f"Flow V1->PFC: {np.mean(gc_v1_to_pfc):.4f}")
```

## Relevant Context / Files
- [analysis-granger-result-extraction](file:///D:/drive/omission/.gemini/skills/analysis-granger-result-extraction/skill.md) — For data extraction logic.
- [analysis-spectrolaminar](file:///D:/drive/omission/.gemini/skills/analysis-spectrolaminar/skill.md) — For regional definition.
