---
name: analysis-granger-convergence-debug
description: Debugs and assesses the convergence of Granger causality analysis for LFP data between specific brain regions (V1 and PFC). This skill systematically tests various model orders to identify potential issues with model stability or parameter selection for Granger causality computations using the Nitime library.
---
# skill: analysis-granger-convergence-debug

## When to Use
Use this skill when Granger causality results appear unstable, contain excessive `NaN` values, or show biologically implausible results. It is specifically designed to:
- Sweep through different Autoregressive (AR) model orders (e.g., 5, 10, 20, 50).
- Identify the "sweet spot" for model complexity where causality estimates stabilize.
- Diagnose failures in the `nitime.analysis.GrangerAnalyzer` engine.

## What is Input
- **LFP Data**: `.npy` files containing multi-channel LFP recordings (e.g., `ses230816-probe2-lfp-AAAX.npy`).
- **Model Orders**: `list` of `int` - AR orders to test.
- **Sampling Rate**: `float` - Typically 1000 Hz.

## What is Output
- **Convergence Metrics**: Printed causality values and `NaN` counts for each order.
- **Directional Analysis**: Comparative causality for V1->PFC vs. PFC->V1 directions.

## Algorithm / Methodology
1. **Signal Aggregation**: Averages multi-channel recordings into a single regional representative signal (V1 and PFC).
2. **Normalization**: Z-scores the signals (mean subtraction, standard deviation division) to ensure model stability.
3. **AR Modeling**: Iteratively fits a Multi-Variate Autoregressive (MVAR) model using `nitime`.
4. **Causality Estimation**: Computes the frequency-domain Granger causality.
5. **Validation**: Checks the integrity of the causality spectrum (checking for non-positive values or `NaN` outputs).

## Placeholder Example
```python
import numpy as np
import nitime.analysis as na
import nitime.timeseries as ts

# 1. Load and Z-score regional signals
v1 = np.load('v1_lfp.npy').mean(axis=(0,1))
pfc = np.load('pfc_lfp.npy').mean(axis=(0,1))
v1 = (v1 - v1.mean()) / v1.std()
pfc = (pfc - pfc.mean()) / pfc.std()

# 2. Test Model Order 20
tseries = ts.TimeSeries(np.stack([v1, pfc]), sampling_rate=1000.0)
analyzer = na.GrangerAnalyzer(tseries, order=20)

# 3. Check for convergence
print(f"NaN count in V1->PFC: {np.isnan(analyzer.causality_xy).sum()}")
```

## Relevant Context / Files
- [debug_granger_convergence.py](file:///D:/drive/omission/codes/scripts/debug_granger_convergence.py) — Source implementation.
- [math-neuro-omission-connectivity-metrics](file:///D:/drive/omission/.gemini/skills/math-neuro-omission-connectivity-metrics/skill.md) — Theoretical background.