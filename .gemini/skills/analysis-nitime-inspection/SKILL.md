---
name: analysis-nitime-inspection
description: Utility for inspecting the output structure and dimensions of `nitime.analysis` components (e.g., GrangerAnalyzer). Used for debugging spectral connectivity pipelines.
---
# skill: analysis-nitime-inspection

## When to Use
Use this skill for rapid sanity checks when building or debugging spectral causality pipelines. It is helpful for:
- Verifying the shape of frequency arrays vs. model orders.
- Confirming channel indexing in `causality_xy` and `causality_yx` matrices.
- Understanding how `nitime` handles multi-channel `TimeSeries` objects before full-scale deployment.

## What is Input
- **TimeSeries Object**: A `nitime.timeseries.TimeSeries` instance.
- **Model Order**: Integer defining the autoregressive (AR) order for Granger analysis.

## What is Output
- **Metadata Log**: Prints shapes and attributes of the `GrangerAnalyzer` result.
- **Spectral Arrays**: Frequency bins and corresponding causality values for all channel pairs.

## Algorithm / Methodology
1. **Object Initialization**: Wraps raw NumPy arrays into `nitime.TimeSeries`.
2. **Analyzer Execution**: Runs `na.GrangerAnalyzer` on the series.
3. **Attribute Parsing**: Specifically inspects:
    - `.frequencies`: The frequency axis.
    - `.causality_xy`: Information flow from channel Y to X.
    - `.causality_yx`: Information flow from channel X to Y.
4. **Validation**: Ensures the number of frequency bins matches `(sampling_rate / 2) + 1` (for standard FFT-based approaches).

## Placeholder Example
```python
import nitime.analysis as na
import nitime.timeseries as ts
import numpy as np

# 1. Create dummy 2-channel data
data = np.random.randn(2, 1000)
tseries = ts.TimeSeries(data, sampling_rate=1000.0)

# 2. Inspect Granger outputs
g_analyzer = na.GrangerAnalyzer(tseries, order=10)
print(f"Frequencies shape: {g_analyzer.frequencies.shape}")
print(f"Causality matrix shape: {g_analyzer.causality_xy.shape}")
```

## Relevant Context / Files
- [analysis-neuro-omission-effective-connectivity](file:///D:/drive/omission/.gemini/skills/analysis-neuro-omission-effective-connectivity/skill.md) — The production pipeline utilizing these inspections.