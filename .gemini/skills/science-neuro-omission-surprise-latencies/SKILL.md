---
name: science-neuro-omission-surprise-latencies
description: Analytical framework for quantifying the temporal onset (latencies) of surprise signals across the hierarchy.
---
# skill: science-neuro-omission-surprise-latencies

## When to Use
Use this skill when performing timing analysis of neural responses. It is mandatory for:
- Calculating the "First Significant Divergence" between Omission and Standard trials.
- Mapping the V1-PFC latency lag to test top-down vs. bottom-up hypotheses.
- Identifying "Prediction-First" areas (where omission latency < stimulus latency).
- Validating the 11-area cortical hierarchy latencies (f044-f045).

## What is Input
- **High-Resolution PSTHs**: 1ms binned firing rates for precise onset detection.
- **Baseline Activity**: Activity during the 200ms pre-stimulus/pre-omission window.
- **Condition Pairs**: Omission (AXAX) vs. Standard (AXAA) at matched sequence positions.

## What is Output
- **Onset Latencies**: Time (ms) to reach significance threshold ($Z > 3$ or $p < 0.05$).
- **Peak Latencies**: Time (ms) of the maximum transient amplitude.
- **Latency Hierarchies**: Ordered list of areas by their surprise detection speed.

## Algorithm / Methodology
1. **Sliding Window T-Test**: Perform a t-test between conditions in a 20ms sliding window (1ms steps).
2. **Persistence Criterion**: Latency is defined as the first bin of $N$ consecutive significant bins (typically $N=20$).
3. **Z-Thresholding**: Alternative method; first bin to exceed $3 \sigma$ of baseline noise.
4. **Hierarchical Comparison**:
   - **Predictive Hubs (FEF/PFC)**: Expect early latencies (~15-45ms).
   - **Sensory Areas (V1/V4)**: Expect late latencies (~100-150ms) if feedback-driven.

## Placeholder Example
```python
import numpy as np

def detect_onset(omit_psth, std_psth, alpha=0.05, consecutive_bins=20):
    """
    Detects the onset of divergence between conditions.
    """
    # Logic to find the first of N consecutive significant bins
    # Returns latency in ms
    return onset_ms

# Example: PFC surprise onset
pfc_onset = detect_onset(pfc_omit_1ms, pfc_std_1ms)
```

## Relevant Context / Files
- [cortical-hierarchy](file:///D:/drive/omission/.gemini/skills/science-neuro-omission-cortical-hierarchy/skill.md) — For the tier-based latency expectations.
- [src/analysis/latencies.py](file:///D:/drive/omission/src/analysis/latencies.py) — The canonical onset detection script.
