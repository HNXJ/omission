---
name: lfp-core
description: Canonical LFP loading, area selection, TFR computation, and plotting guidance for the omission repo.
triggers:
  - extract LFP by area or condition
  - compute omission-aligned TFRs
  - reuse canonical LFP functions
owners:
  - codes/functions/io/lfp_io.py
  - codes/functions/lfp/lfp_pipeline.py
  - codes/functions/lfp/lfp_mapping.py
  - codes/functions/lfp/lfp_tfr.py
  - codes/functions/visualization/lfp_plotting.py
  - codes/functions/visualization/poster_figures.py
entrypoints:
  - codes/functions/io/lfp_io.py::load_session
  - codes/functions/lfp/lfp_pipeline.py::get_signal_conditional
  - codes/functions/lfp/lfp_tfr.py::compute_tfr
outputs:
  - area-filtered LFP epochs
  - time-frequency power arrays
  - band-collapsed trajectories
limitations:
  - do not rely on Granger unless lfp_connectivity.py is repaired and validated
  - do not present lfp_preproc.py as stable if it is still parse-broken
---

# SKILL: lfp-core

## Use this when
- you need omission-task LFP for a specific area
- you need p1-aligned epochs for plotting or summary analysis
- you want to reuse the repo’s canonical TFR functions instead of writing new loaders

## Do not use this when
- you need behavioral trial extraction from MonkeyLogic files
- you need unit-only analyses without LFP
- you need manuscript-ready Granger without first validating connectivity code

## Repo truths
- displayed event time is p1-relative milliseconds
- canonical area order is V1, V2, V3d, V3a, V4, MT, MST, TEO, FST, FEF, PFC
- multi-area probes must follow deterministic split logic from the mapping rules

## Primary files
- `codes/functions/io/lfp_io.py` — NWB session loading and manifest saving
- `codes/functions/lfp/lfp_pipeline.py` — canonical public accessor `get_signal_conditional(...)`
- `codes/functions/lfp/lfp_mapping.py` — deterministic area membership mapping
- `codes/functions/lfp/lfp_tfr.py` — spectral decomposition and band collapse

## Execution steps
1. Use `load_session()` to inspect whether LFP and electrode metadata exist.
2. Use `get_signal_conditional()` for area-specific extraction instead of custom slicing.
3. Use `compute_tfr()` and `collapse_band_power()` for spectral summaries.
4. Use plotting helpers instead of re-implementing event timing patches.

## Validate before trusting results
- confirm area labels are canonical after mapping
- confirm displayed times are p1-relative and not raw sample indices
- confirm extracted epoch shapes match trials × channels × time
- confirm missing or partial preprocessing is disclosed if bypassed

## Common failure modes
- no channels found for area -> audit session mapping first
- parse error in `lfp_preproc.py` -> bypass or repair before claiming a full preprocessing pipeline
- placeholder connectivity code -> do not report Granger results as final

## Output contract
- report the session, area, signal type, window, and array shape used
- save derived outputs only in appropriate analysis/output paths, not the repo root

## Minimal examples
```python
from pathlib import Path
from codes.functions.lfp.lfp_pipeline import get_signal_conditional
from codes.functions.lfp.lfp_tfr import compute_tfr, collapse_band_power

epochs = get_signal_conditional(Path("data/nwb/sub-...nwb"), area="V1", signal_type="LFP")
freqs, times_ms, power = compute_tfr(epochs.mean(axis=1))
bands = collapse_band_power(freqs, power)
```
