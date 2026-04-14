---
name: analysis-nwb-read-guardrails
description: Mandatory read-side guardrails for all NWB-based analysis in the omission repo. Protects frozen source data while improving speed through lazy reads, one-open-per-session patterns, and external metadata caches.
---

# skill: analysis-nwb-read-guardrails

## scope
Applies to any task that:
- opens `.nwb` files
- reads trials/electrodes/units tables
- slices LFP or behavioral streams
- builds trial-aligned arrays
- computes per-session metadata maps

## hard constraints
- The NWB files are frozen.
- Never rewrite, export, rechunk, recompress, or modify source NWB files.
- Preserve compatibility with existing data fields exactly as stored.
- Prefer read-side optimization only: lazy slicing, one-open-per-session, and external derived caches.
- Any optimization must leave raw NWB content untouched.

## preferred pattern
- Open each NWB file once per session-level task and reuse the opened content within that task.
- Treat `TimeSeries.data` as lazy/on-disk; slice only the time/channel region needed.
- Use `to_dataframe()` only when downstream logic truly needs pandas-style joins, filtering, or grouping.
- In hot paths, prefer direct column access or precomputed sidecar metadata over repeated full-table conversion.
- Precompute once per session:
  - trial index / p1 onsets
  - area -> channel indices
  - unit -> probe map
  - unit -> area map
- Write any derived cache outside the NWB file, with provenance metadata.

## anti-patterns
- Do not call `np.asarray(series.data)` on full LFP just to inspect shape.
- Do not reopen the same NWB file inside area loops, condition loops, plotting loops, or helper functions called from those loops.
- Do not call `to_dataframe()` repeatedly for the same table inside inner loops.
- Do not sanitize full-session datasets with `np.nan_to_num` before slicing; sanitize only the in-memory slice or epoch being analyzed.
- Do not use export/rewrite workflows as a performance shortcut.

## done when
- One NWB open per session task.
- No repeated trial-table parse in inner loops.
- No full-session LFP materialization unless the task explicitly requires the full session matrix.
- Any new derived cache is written outside the NWB file with clear provenance metadata.
