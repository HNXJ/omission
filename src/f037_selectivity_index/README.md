# f037: Stimulus Selectivity Index (SSI)

## Overview
Computes the Stimulus Selectivity Index (SSI) for neurons during the omission window. This allows us to determine if neural surprise signals are restricted to the expected stimulus pathway.

## What is Input
- **Units**: 'Stable-Plus' population (FR > 1Hz, SNR > 0.8).
- **Spike Data**: 6000ms aligned spike arrays from `loader.load_unit_spikes`.
- **Condition**: AXAB sequence (p1=Predictable B, p2=Omission B).
- **Window**: Ghost window (0 to 500ms post-omission).

## What is Output
- **Metrics**: 
  - `ssi_mean`: Mean selectivity across the population in an area.
  - `ssi_sem`: Standard error of the mean.
- **Figures**: 
  - `Export_Staging/f037_selectivity_index.html`: Interactive bar plot showing SSI across brain areas.

## Usage
```python
from src.f037_selectivity_index.analysis import analyze_selectivity_index
results = analyze_selectivity_index(loader, ["V1", "PFC"])
```

## Example
High SSI in V1 Superficial layers suggests that prediction errors are highly specific to the missing stimulus identity.
