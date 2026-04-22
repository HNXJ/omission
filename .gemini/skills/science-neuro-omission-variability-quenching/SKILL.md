---
name: science-neuro-omission-variability-quenching
description: Analytical framework for quantifying trial-to-trial variability reduction (Quenching) using Mean-Matched Fano Factor (MMFF).
---
# skill: science-neuro-omission-variability-quenching

## When to Use
Use this skill when assessing neural state stability or precision. It is mandatory for:
- Calculating the Fano Factor ($FF = \sigma^2 / \mu$) across trials.
- Performing "Mean-Matching" to decouple variability changes from firing rate changes.
- Testing the "Precision-Update" hypothesis (omission triggers stronger quenching for the next stimulus).
- Comparing quenching magnitudes across layers and areas.

## What is Input
- **Spike Counts**: Number of spikes per trial in a sliding window (e.g., 50ms).
- **Trial Metadata**: Condition labels to group trials for variance calculation.
- **Unit Population**: A large set of units to allow for robust mean-matching subsampling.

## What is Output
- **MMFF Curves**: Time-resolved Fano Factor after controlling for mean firing rates.
- **Quenching Onset**: The time at which variability significantly drops below pre-stimulus levels.
- **Precision Metrics**: Magnitude of variability reduction as a proxy for internal model precision.

## Algorithm / Methodology
1. **Raw Statistics**: Compute the mean and variance of spike counts across trials for each unit and time bin.
2. **Mean-Matching (Churchland Method)**:
   - Create a 2D scatter plot of Variance vs. Mean for all units/bins.
   - For each mean value, find a subset of points that have a balanced distribution across conditions.
   - Compute the slope of the regression line on the mean-matched subset.
3. **Condition Contrast**: Compare quenching during Omissions (AXAX) vs. Standards (AXAA).
4. **Post-Omission Effect**: Quantify if the quenching on the *next* stimulus (P3) is enhanced by a preceding omission.

## Placeholder Example
```python
import numpy as np

def compute_fano_factor(spike_counts):
    """
    Computes raw Fano Factor.
    spike_counts: (trials, units, time)
    """
    mu = np.mean(spike_counts, axis=0)
    var = np.var(spike_counts, axis=0)
    return var / (mu + 1e-9)

# Example: V1 quenching during stimulus onset
ff_v1 = compute_fano_factor(v1_spikes)
```

## Relevant Context / Files
- [active-inference](file:///D:/drive/omission/.gemini/skills/science-neuro-omission-active-inference/skill.md) — For the interpretation of quenching as precision-weighting.
- [src/analysis/fano_factor.py](file:///D:/drive/omission/src/analysis/fano_factor.py) — The canonical MMFF implementation.
