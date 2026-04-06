## gemini project context: omission

**Project root**: `D:\drive\omission/`  
**Repo**: `hnxj/omission` | **Profile**: @hnxj

---

## directory structure
```
codes/
  functions/    # importable modules (underscores in filenames)
  scripts/      # run-able entrypoints (hyphens in filenames)
context/
  docs/         # poster descriptions, reference documents
  plans/        # analysis plans and roadmaps
  queue/        # pending tasks
gemini.md       # this file
vmemory.md      # methodology memory
```

## analysis pipeline: 15-step lfp protocol
**Module**: `codes/functions/lfp_pipeline.py`  
**Plan**: `context/plans/15-step-lfp-pipeline.md`

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `validate_session_schema` | NWB schema enforcement |
| 2 | `build_omission_windows` | event timeline + ghost signal |
| 3 | `run_lfp_qc` | per-channel QC |
| 4 | `extract_matched_epochs` | trial-aligned epochs |
| 5 | `normalize_epochs` | dB baseline normalization |
| 6 | `compute_tfr_per_condition` | TFR per area per condition |
| 7 | `compute_band_contrast` | omission Δ-power per band |
| 8 | `compute_spectral_corr` | inter-area correlation matrices |
| 9 | `compute_all_pairs_coherence` | all-pairs coherence spectra |
| 10 | `build_coherence_network_data` | adjacency matrices per band |
| 11 | `compute_spectral_granger` | directional GC (VAR-based) |
| 12 | `run_cluster_permutation` | cluster permutation stats |
| 13 | `aggregate_by_tier` | Low/Mid/High hierarchy tiers |
| 14 | `compute_post_omission_adapt` | post-omission trial tracking |
| 15 | `write_analysis_manifest` | JSON + CSV reproducibility |

## core function modules
| Module | Contents |
|--------|----------|
| `lfp_constants.py` | Colors, timing, bands, `FS_LFP=1000.0` |
| `lfp_io.py` | load_session, load_condition_table, save_json_manifest |
| `lfp_events.py` | build_event_table, infer_omission_position |
| `lfp_preproc.py` | apply_bipolar_ref, baseline_normalize, extract_epochs |
| `lfp_tfr.py` | compute_tfr, get_band_power, collapse_band_power |
| `lfp_stats.py` | mean_sem, run_cluster_permutation, run_tier_rank_sum |
| `lfp_connectivity.py` | compute_coherence, compute_granger |
| `lfp_plotting.py` | create_tfr_figure, plot_tfr_grid, create_band_plot |
| `lfp_pipeline.py` | **15-step pipeline** — new master module |
| `poster_figures.py` | Exact poster figure replication (10 figure functions) |

## constants (authoritative)
```python
FS_LFP = 1000.0   # Hz
Beta = (13, 30)   # widened per protocol
fx = -500ms       # fixation pre-window (baseline)
p1 = 0ms          # alignment anchor (code 101.0)
Normalization = dB (10*log10(P/Pbase))
```

## aesthetic mandates
- **Palette**: Gold=`#CFB87C`, Violet=`#8F00FF`, Black=`#000000`
- **Theme**: `plotly_white`, Arial font
- **Condition colors**: RRRR=Gold, RXRR=Violet, RRXR=Teal, RRRX=Orange
- **SEM**: ±2 SEM on all band-power and spiking traces
- **Safety**: Never save NaN/all-zero plots. Log to `context/queue/`.

## skills (26 active)
`analysis-lfp-pipeline`, `analysis-lfp-15step`, `analysis-poster-figures`,
`analysis-poster-figure-pipeline`, `analysis-mmff`, `analysis-population-coding`,
`analysis-rsa-cka`, `predictive-routing`, `analysis-spectrolaminar`,
`analysis-nwb-utils` + 16 others in `.gemini/skills/`

## active objectives
- **OMISSION-LFP (P1)**: Run 15-step pipeline across all 13 sessions
- **FIGURES (P1)**: Generate revision panels using `poster_figures.py`
- **MLLM (P1)**: Monitor M3-Max Office Mac

## rules (immutable)
- **Root Integrity**: No new folders or files are allowed in the root of any git directory unless specifically requested and confirmed.
- **Context Only**: Only code and markdown files are allowed in the `omission/` repository.
- **Naming**: No uppercase in filenames or function names; no underscores in `codes/scripts/` (use hyphens).
- **Versioning**: No version suffixes (`_v1`, `_v2`, `_final`) anywhere.
- **Functions**: All function names must be ≤49 characters.
- **Outputs**: All analysis outputs (`.html`, `.svg`, `.npy`, `.metadata.json`) must go to `output/` (outside repo root).
- **Structure**: `codes/functions/` for imports, `codes/scripts/` for entrypoints.
- **Documentation**: All non-code context belongs in `context/` as organized markdown.
