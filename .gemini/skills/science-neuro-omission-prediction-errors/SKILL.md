---
name: science-neuro-omission-prediction-errors
description: Theoretical and analytical framework for quantifying "Surprise" (prediction error) signals during sequence violations.
---
# skill: science-neuro-omission-prediction-errors

## When to Use
Use this skill when identifying and quantifying neural transients triggered by unexpected events. It is mandatory for:
- Calculating the magnitude of "Omission Transients" relative to standard stimulus responses.
- Testing the "Deviance-Scaling" hypothesis (f035) — proportionality to statistical rarity.
- Identifying the onset and peak timing of the surprise signal across areas.
- Dissociating "Stimulus-Off" transients from "Prediction-Error" transients.

## What is Input
- **Trial-Averaged PSTHs**: Conditioned on Standard (AXAA) vs. Omission (AXAX).
- **Surprisal Values**: Bit-values assigned to each trial type based on block statistics.
- **Unit Indices**: Functional labels (S+/O+) to isolate units that specifically track errors.

## What is Output
- **Surprise Magnitudes**: Normalized differences in firing rates (Omission - Standard).
- **Deviance-Scaling Slopes**: Linear fit of neural response magnitude vs. information-theoretic surprisal.
- **Detection Hubs**: Areas/layers showing the earliest or most robust error signals (typically PFC/FEF).

## Algorithm / Methodology
1. **Transient Baseline**: Subtract the baseline firing rate (gray-screen period) from the post-omission transient.
2. **Standard Contrast**: Compare the omission response to the response at the same sequence position in a standard trial.
3. **Scaling Analysis**: Group trials by surprise level (10% omission vs. 30% omission) and test for monotonic scaling.
4. **Latency Mapping**: Identify the earliest area to cross the significance threshold ($Z > 3$) for the omission effect.

## Placeholder Example
```python
import numpy as np

def calculate_surprise_index(omit_rate, std_rate):
    """
    Computes the normalized surprise index.
    Index > 0 implies an enhancement (Prediction Error).
    """
    return (omit_rate - std_rate) / (omit_rate + std_rate + 1e-6)

# Example: Surprise index for a PFC unit at P4 position
idx = calculate_surprise_index(rate_p4_omit, rate_p4_std)
```

## Relevant Context / Files
- [active-inference](file:///D:/drive/omission/.gemini/skills/science-neuro-omission-active-inference/skill.md) — For the theoretical grounding of these errors.
- [src/math/surprise_scaling.py](file:///D:/drive/omission/src/math/surprise_scaling.py) — The regression engine for scaling tests.
