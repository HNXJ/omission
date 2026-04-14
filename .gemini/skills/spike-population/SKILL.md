---
name: spike-population
description: Unit extraction, population summaries, variability, and hierarchy-wide dynamics analysis.
triggers:
  - extract unit traces by session
  - compute area-based Fano factor
  - analyze spike-population dynamics
owners:
  - codes/functions/spiking/omission_hierarchy_utils.py
  - codes/functions/spiking/spike_lfp_coordination.py
  - codes/functions/utilities/extract_omission_factors.py
entrypoints:
  - codes/functions/spiking/omission_hierarchy_utils.py::extract_unit_traces
  - codes/functions/spiking/omission_hierarchy_utils.py::compute_area_mmff
outputs:
  - firing rate traces
  - population Fano factor trajectories
  - unit-to-area mappings
limitations:
  - MMFF calculation assumes smoothed traces as input proxies
  - requires well-curated NWB units table
---

# SKILL: spike-population

## Use this when
- you need population-level spiking dynamics or variability analysis
- you need to categorize neurons into omission-responsive vs. non-responsive
- you need hierarchical area mapping (V1-PFC)

## Do not use this when
- you need raw LFP spectral power (use lfp-core)
- you need behavioral decoding (use eye-behavior)

## Repo truths
- canonical area order: V1, V2, V3d, V3a, V4, MT, MST, TEO, FST, FEF, PFC
- unit mapping follows deterministic area rules in omission_hierarchy_utils.py

## Primary files
- `codes/functions/spiking/omission_hierarchy_utils.py` — canonical unit mapping and MMFF logic
- `codes/functions/spiking/spike_lfp_coordination.py` — PPC and phase-locking primitives

## Execution steps
1. Use `get_unit_to_area_map()` to verify unit assignment to cortical areas.
2. Use `extract_unit_traces()` for firing rate and variance time series.
3. Apply `compute_area_mmff()` for population-level variability trends.

## Validate before trusting results
- ensure unit quality filtering is applied
- verify trial/condition subsets match the research plan (P2/P3/P4)

## Output contract
- results saved as standardized .npy or .json structures in `outputs/`
- reports must specify the subset of units used

## Minimal examples
```python
from codes.functions.spiking.omission_hierarchy_utils import extract_unit_traces
traces = extract_unit_traces(session_id="230629")
```
