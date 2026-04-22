---
name: analysis-omission-factor-extraction
description: Pipeline for extracting 48 specific neural features (factors) per neuron. Features include mean firing rates, ISI statistics, and cross-trial variability across conditions.
---
# skill: analysis-omission-factor-extraction

## When to Use
Use this skill when building the master feature matrix for population-level classification or regression. It is the primary tool for:
- Characterizing neuron-specific responses to predictable vs. omitted stimuli.
- Quantifying the "surprise" response through firing rate changes in the `omit` window.
- Preparing high-dimensional datasets for R-based factor analysis or decoding.
- Validating laminar differences in stimulus-driven vs. prediction-driven units.

## What is Input
- **NWB Files**: For unit-to-area mapping and anatomical metadata.
- **Spike Arrays**: Binned spike matrices `(trials, units, time)` from `data/arrays/`.
- **Layer CSV**: Layer assignments from `checkpoints/real_omission_units_layered_v3.csv`.

## What is Output
- **Feature CSV**: `checkpoints/omission_neurons_r_factors.csv` containing 48 features per neuron.
- **Factor Matrix**: A Pandas DataFrame ready for statistical analysis in R.

## Algorithm / Methodology
1. **Mapping**: Reconciles unit indices across NWB files and .npy arrays using `probe_id` and `local_idx`.
2. **Feature Windows**: Identifies four temporal windows: `fx` (baseline), `pre` (stimulus), `omit` (omission), and `post` (recovery).
3. **Condition Masking**: Loops through specific trial sequences: `RXRR`, `RRXR`, and `RRRX`.
4. **Metric Calculation**: For each unit/condition/window, computes:
    - **Mean FR**: Average spikes/sec.
    - **STD ISI**: Variability of inter-spike intervals.
    - **Cross-Trial Var**: Mean and STD of the variance across trials (FF-related).
5. **Serialization**: Flattens the feature vector and saves with session/area/layer identifiers.

## Placeholder Example
```python
from src.extract.omission_factors import extract_factors

# 1. Run extraction for all sessions
df_factors = extract_factors(nwb_dir="data/nwb/", array_dir="data/arrays/")

# 2. Inspect output
print(df_factors.columns) # 48 feature columns + metadata
print(df_factors[['session', 'area', 'RRXR_omit_mean_fr']].head())
```

## Relevant Context / Files
- [analysis-neuro-omission-unit-classification](file:///D:/drive/omission/.gemini/skills/analysis-neuro-omission-unit-classification/skill.md) — For unit type definitions.
- [src/extract/extract_omission_factors.py](file:///D:/drive/omission/src/extract/extract_omission_factors.py) — Core logic implementation.