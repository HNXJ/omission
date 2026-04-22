---
name: analysis-neuro-omission-unit-classification
description: Categorizes neurons into functional types (S+, O+, S-, O-) based on response profiles. Implements the Top 10 indexing rule for high-fidelity population analysis.
---
# skill: analysis-neuro-omission-unit-classification

## When to Use
Use this skill to functionally segment the neural population. It is critical for:
- Identifying "Error Neurons" (O+) in PFC/FEF.
- Mapping "Stimulus Drivers" (S+) in early visual areas.
- Generating Figure 7 (Spike-Field Coupling) by selecting the most representative units.
- Testing hierarchical predictive coding (Feedforward S+ vs. Feedback O+).

## What is Input
- **Spike Matrix**: `(n_trials, n_units, n_time_bins)`.
- **Epoch Definitions**: 
    - `fx`: Fixation (-500 to 0ms)
    - `p1`: First Stimulus (0 to 531ms)
    - `d1`: First Delay (531 to 1031ms)
    - `p2`: Omission Window (1031 to 1562ms)

## What is Output
- **Unit Labels**: Dictionary mapping unit IDs to functional categories (S+, O+, etc.).
- **Ranking Scores**: Z-scores or fold-change ratios for Stimulus and Omission responsiveness.
- **Top 10 Indices**: The 10 most responsive units per area for both S+ and O+ types.

## Algorithm / Methodology
1. **Response Calculation**: Computes mean firing rates for the four critical epochs (`fx`, `p1`, `d1`, `p2`).
2. **S+ Indexing**: `Score_S = Mean(p1) / (Mean(fx) + epsilon)`. Units with max `Score_S` are S+.
3. **O+ Indexing**: `Score_O = Mean(p2) / (Mean(d1) + epsilon)`. Units with max `Score_O` are O+.
4. **Classification**: 
    - S+ if `Score_S` > threshold and `Score_S > Score_O`.
    - O+ if `Score_O` > threshold and `Score_O > Score_S`.
5. **Top 10 Selection**: Sorts all units within a brain area by their respective scores and selects the top 10 for detailed analysis (e.g., SFC).

## Placeholder Example
```python
import numpy as np
from src.analysis.classification import get_top_units

# 1. Load spike data
spk_matrix = load_session_spikes(session_id)

# 2. Get Top 10 Omission units for PFC
top_o_pfc = get_top_units(spk_matrix, area='PFC', type='O+', top_n=10)

# 3. Verify selection
print(f"Indices of Top 10 PFC Omission neurons: {top_o_pfc}")
```

## Relevant Context / Files
- [src/analysis/classification.py](file:///D:/drive/omission/src/analysis/classification.py) — Core logic for S+/O+ indexing.
- [analysis-neuro-omission-functional-connectivity](file:///D:/drive/omission/.gemini/skills/analysis-neuro-omission-functional-connectivity/skill.md) — For mapping these units to SFC.
