# 15-step lfp omission analysis pipeline

**Source**: `codes/functions/lfp_pipeline.py`  
**Skill**: `.gemini/skills/analysis-lfp-15step/skill.md`

---

## step 1 — nwb lfp schema validation
**Function**: `validate_session_schema(session)`  
Enforces canonical session dict: `{session_id, nwb_path, lfp, electrodes, trials, areas, channels, photodiode, fs, channel_depths, channel_areas}`. Returns `(session, qc_flags)`. Alignment anchor: code 101.0 = p1 = 0ms. All downstream steps depend on this schema.

## step 2 — event timeline and omission windows
**Functions**: `build_omission_windows(event_table, ...)` + `lfp_events.build_event_table`  
Builds per-trial windows for baseline `(-500, 0ms)`, stimulus `(0, 531ms)`, and omission. Encodes "ghost signal": omission timing = expected stimulus onset. Stores both absolute and p1-relative times. Output: `{windows, ghost_times, stimulus_win, baseline_win, by_trial}`.

## step 3 — lfp quality control and bipolar referencing
**Function**: `run_lfp_qc(lfp, fs, ...)`  
Reports per-channel variance, flat channels, 60Hz line-noise burden, NaN fraction. Flags: `passed=True` if <10% channels are bad. Called BEFORE bipolar referencing. Follow with `lfp_preproc.apply_bipolar_ref`.

## step 4 — aligned epoch extraction
**Function**: `extract_matched_epochs(lfp_by_area, event_table, omission_windows, ...)`  
Returns `{area: {condition: array(n_trials, n_ch, n_times)}}`. Window: default `(-500, 4200ms)`. For each omission trial produces a matched control window from same session. Warns if n_trials < 10.

## step 5 — baseline normalization
**Function**: `normalize_epochs(epochs_by_area, baseline_win_ms=(-500,0), method='db')`  
Three methods: `'db'` = 10·log₁₀(P/Pbase) [**default — matches poster**], `'pct'` = percent change, `'zscore'` = trial-wise. Same scale applied across all conditions and areas.

## step 6 — time-frequency representations
**Function**: `compute_tfr_per_condition(epochs_by_area, ...)`  
Hanning window, 98% overlap (nperseg=256, noverlap=251), scipy.signal.spectrogram. Output: `{area: {condition: (freqs, times_ms, power_db)}}`. Standard range: 1–150Hz.

## step 7 — band power omission contrast
**Function**: `compute_band_contrast(tfr_by_area, omission_cond, control_cond, ...)`  
Computes Δ = omission − control per band per area. Negative delta in Alpha/Beta = dampening. Near-zero Gamma = poster finding. Bands: Theta(4-8), Alpha(8-13), Beta(13-30), Gamma(35-70).

## step 8 — spectral correlation matrices
**Function**: `compute_spectral_corr(band_power_by_area, areas, window_slice)`  
Returns (n_areas × n_areas) Pearson-r matrix. Compute separately for stimulus `(0–531ms)` and omission windows. Feed to `plot_spectral_corr_matrices` in `poster_figures.py`.

## step 9 — inter-area coherence spectra
**Function**: `compute_all_pairs_coherence(lfp_by_area, areas, fs, ...)`  
All i<j area pairs via `scipy.signal.coherence`. Returns `{(area_i, area_j): (freqs, cxy)}`. Use bipolar LFP as input. Separate calls for stimulus window and omission window.

## step 10 — coherence network adjacency
**Function**: `build_coherence_network_data(coh_pairs, areas, band='Beta')`  
Collapses coherence spectra to band-limited adjacency matrix (n_areas × n_areas). Feed to `plot_spectral_network` in `poster_figures.py`. Compute separately for Beta (omission) and Gamma (stimulus) to show spectral harmony flip.

## step 11 — spectral granger causality
**Function**: `compute_spectral_granger(sig_source, sig_target, fs, max_lag=50, ...)`  
Bivariate VAR-based spectral GC (Wilson 1972). Returns `gc_xy` (feedforward) and `gc_yx` (feedback) per frequency. `net_dir = gc_xy - gc_yx` (positive = feedforward dominance). Uses statsmodels VAR with BIC lag selection.

## step 12 — cluster permutation statistics
**Function**: `run_cluster_permutation(x, y, n_perm=1000, threshold_p=0.05)` in `lfp_stats.py`  
Real implementation: per-point t-test → threshold → find clusters → permutation null distribution → cluster p-values → boolean mask. Apply to TFR contrasts and band power trajectories.

## step 13 — hierarchy tier aggregation
**Function**: `aggregate_by_tier(measures_by_area, tiers, agg='mean')`  
Aggregates any scalar or array per area into Low/Mid/High cortical tiers. Returns `{tier: {mean, sem, median, n, areas}}`. Use `run_tier_rank_sum` from `lfp_stats.py` for significance.  
Tiers default: Low=[V1,V2], Mid=[V4,MT,MST,TEO,FST], High=[V3A,V3D,FEF,PFC].

## step 14 — post-omission adaptation
**Function**: `compute_post_omission_adapt(band_power_by_trial, omission_trial_idx, n_post=5)`  
Returns `{band: array(n_post+1, n_times)}`. Row 0 = omission trial; rows 1..n_post = subsequent trials. Tests whether beta synchrony persists (lasting state) vs. recovers (1-trial perturbation).

## step 15 — analysis manifest
**Function**: `write_analysis_manifest(out_dir, session_id, figure_specs, analysis_params, band_data)`  
Writes: `{session_id}_manifest.json` + `{session_id}_band_summary.csv`. Every figure must trace to a manifest entry. Manifest records: fs, nperseg, band ranges, alignment, normalization method, conditions used per figure.

---

## timing standards (all steps)
| Event | Time (ms re p1) |
|-------|-----------------|
| fx onset | -500 |
| p1 onset | 0 |
| d1 onset | 531 |
| p2 onset | 1031 |
| d2 onset | 1562 |
| p3 onset | 2062 |
| d3 onset | 2593 |
| p4 onset | 3093 |
| d4 onset | 3624 |

## band definitions (updated)
| Band | Freq (Hz) |
|------|-----------|
| Theta | 4–8 |
| Alpha | 8–13 |
| **Beta** | **13–30** |
| Gamma | 35–70 |
