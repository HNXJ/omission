---
name: analysis-lfp-15step
description: Complete 15-step LFP-only omission analysis pipeline. Orchestrates NWB loading, QC, bipolar ref, epoch extraction, dB normalization, TFR, band-contrast, spectral correlation, coherence, network graphs, spectral Granger, cluster permutation, tier aggregation, post-omission adaptation, and manifest writing.
source: codes/functions/lfp_pipeline.py
cross-ref: analysis-lfp-pipeline (individual modules), analysis-poster-figures (figure rendering)
plan: context/plans/15-step-lfp-pipeline.md
---

# skill: analysis-lfp-15step

## function map

| Step | Function | Input → Output |
|---|---|---|
| 1 | `validate_session_schema(session)` | raw session dict → validated dict + qc_flags |
| 2 | `build_omission_windows(event_table)` | events df → {windows, ghost_times, by_trial} |
| 3 | `run_lfp_qc(lfp, fs)` | raw LFP → {passed, flat_ch, noisy_ch, variance} |
| 4 | `extract_matched_epochs(lfp_by_area, events, ...)` | LFP + events → {area: {cond: (n,ch,T) array}} |
| 5 | `normalize_epochs(epochs, method='db')` | epochs → dB-normalized epochs |
| 6 | `compute_tfr_per_condition(epochs)` | epochs → {area: {cond: (freqs, times_ms, pwr_db)}} |
| 7 | `compute_band_contrast(tfr, omit, ctrl)` | TFR dict → {area: {band: delta_array}} |
| 8 | `compute_spectral_corr(band_power, areas)` | {area: (n_trials,T)} → (n×n) Pearson-r matrix |
| 9 | `compute_all_pairs_coherence(lfp, areas)` | LFP dict → {(ai,aj): (freqs, cxy)} |
| 10 | `build_coherence_network_data(coh_pairs, areas, band)` | coh pairs → (n×n) adjacency matrix |
| 11 | `compute_spectral_granger(sig_src, sig_tgt)` | two 1D signals → {gc_xy, gc_yx, net_dir} |
| 12 | `run_cluster_permutation(x, y, n_perm)` | `lfp_stats.py` → {mask, cluster_p, tstat} |
| 13 | `aggregate_by_tier(measures_by_area)` | {area: val} → {Low/Mid/High: {mean, sem}} |
| 14 | `compute_post_omission_adapt(pwr_by_trial, omit_idx)` | trial array → {band: (n_post, n_times)} |
| 15 | `write_analysis_manifest(out_dir, session_id, ...)` | params + specs → JSON + CSV |

## canonical pipeline call
```python
from pathlib import Path
from codes.functions.lfp_io import load_session, load_condition_table
from codes.functions.lfp_events import build_event_table
from codes.functions.lfp_preproc import apply_bipolar_ref
from codes.functions.lfp_pipeline import (
    validate_session_schema, build_omission_windows, run_lfp_qc,
    extract_matched_epochs, normalize_epochs, compute_tfr_per_condition,
    compute_band_contrast, compute_spectral_corr, compute_all_pairs_coherence,
    build_coherence_network_data, aggregate_by_tier, write_analysis_manifest,
)
from codes.functions.lfp_constants import AREA_ORDER, FS_LFP

nwb = Path("data/session_230629.nwb")
session  = load_session(nwb)
session, qc = validate_session_schema(session)
events   = build_event_table(session)
windows  = build_omission_windows(events)
qc_rep   = run_lfp_qc(session['lfp'], fs=FS_LFP)
lfp_ref  = {a: apply_bipolar_ref(lfp_by_area[a]) for a in AREA_ORDER}
epochs   = extract_matched_epochs(lfp_ref, events, windows)
normed   = normalize_epochs(epochs, method='db')
tfr      = compute_tfr_per_condition(normed)
contrast = compute_band_contrast(tfr, 'RXRR', 'RRRR')
coh      = compute_all_pairs_coherence(lfp_ref, AREA_ORDER)
adj_beta = build_coherence_network_data(coh, AREA_ORDER, band='Beta')
tiers    = aggregate_by_tier({a: contrast[a]['Beta'].mean() for a in contrast})
write_analysis_manifest(Path('output/230629'), '230629')
```

## key constants (authoritative)
```python
FS_LFP = 1000.0
Beta   = (13, 30)   # widened from 15-25
fx     = -500ms     # baseline window start (corrected from -1000)
p1     = 0ms        # alignment anchor (code 101.0)
```

## validation rules
- `validate_session_schema` must be called first — all steps depend on its schema
- `run_lfp_qc` before `apply_bipolar_ref` — flag bad channels before pairing
- n_perm ≥ 1000 for `run_cluster_permutation` in final analyses
- All outputs checked: if any array is all-NaN or all-zero → skip + log to `context/queue/`
