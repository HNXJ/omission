---
name: analysis-lfp-pipeline
description: Modular LFP pipeline for sequential visual omission tasks. Covers NWB loading, bipolar referencing, TFR, connectivity, and Plotly visualization standards.
---

# skill: analysis-lfp-pipeline

## architecture (codes/functions/)
- `lfp_io`: NWB/NPY loading with mandatory `np.nan_to_num` sanitation.
- `lfp_events`: Canonical timeline reconstruction aligned to p1 onset (0ms).
- `lfp_preproc`: Bipolar referencing, baseline normalization (% dB change), epoch extraction.
- `lfp_tfr`: Hanning-windowed spectrograms — 98% overlap, 1–150Hz, ms x-axis.
- `lfp_connectivity`: Pairwise coherence and spectral Granger causality (order=15 AR).
- `lfp_plotting`: Standardized Plotly visualizations with sequence rectangle patches.
- `lfp_constants`: `SEQUENCE_TIMING` dict with start/end/color per event.

## standards
- **Timing**: p1 = 0ms (Sample 1000). p2 = 1031ms, p3 = 2062ms, p4 = 3093ms.
- **Sanitation**: `np.nan_to_num` on all LFP arrays before any operation.
- **Normalization**: dB change — `10*log10(P/P_baseline)` vs. fixation window (-500 to 0ms).
- **Connectivity**: Spectral Granger, Ch0=V1 Ch1=PFC pairwise. PLI and Coherence for cross-area.
- **PPC**: Pairwise Phase Consistency for spike-field coupling (firing-rate bias free).
- **Reproducibility**: Save `.metadata.json` sidecar for every derived `.npy` array.

## plotting standards (revision v4)
- **Theme**: `plotly_white`, Arial font, pure black axes.
- **Time axis**: Always ms. Aligned to p1 (0ms).
- **Bands**: Theta 4–8Hz, Alpha 8–14Hz, Beta 15–30Hz, Low-γ 35–55Hz, High-γ 65–100Hz.
- **Patches**: Gold p1, Violet p2, Teal p3, Orange p4, Gray delays (see `lfp_constants.SEQUENCE_TIMING`).
- **Variability**: ±2SEM shaded regions on all power traces.
- **Spectrograms**: dB normalization; zsmooth='best' for heatmaps.
- **Fig catalog**: Fig05=TFR heatmap, Fig06=Band traces, Fig07=Spike-LFP corr, Fig08=Quenching.

## quick start
```python
from codes.functions.lfp_io import load_session
from codes.functions.lfp_events import build_event_table
from codes.functions.lfp_preproc import apply_bipolar_ref

session = load_session(Path("session.nwb"))
events  = build_event_table(session)
lfp_bip = apply_bipolar_ref(session["lfp"])
```


---

## lfp_io — full api
| Function | Purpose |
|---|---|
| `load_session(nwb_path)` | Opens NWB file, returns session dict with lfp/units/trials |
| `load_condition_table(root, session_id, cond)` | Loads `.npy` spike/lfp/behavioral array for a condition |
| `save_json_manifest(path, meta_dict)` | Writes `.metadata.json` sidecar next to any derived array |
| `save_lfp_results(out_path, data, meta)` | Saves derived LFP `.npy` + auto-generates sidecar |

## lfp_events — full api
| Function | Purpose |
|---|---|
| `build_event_table(session)` | Returns DataFrame of all event codes with ms timestamps |
| `infer_omission_position(condition)` | Returns 2, 3, or 4 given cond string (e.g. 'RXRR' → 2) |

## lfp_preproc — full api
| Function | Purpose |
|---|---|
| `preprocess_lfp(lfp, fs)` | Full pipeline: bipolar ref → baseline normalize → epoch extract |
| `apply_bipolar_ref(lfp)` | Adjacent-channel subtraction (shape: `(ch, T)` → `(ch-1, T)`) |
| `baseline_normalize(epoch, baseline_win)` | dB change: `10*log10(P/P_baseline)`, fixation window -500–0ms |
| `extract_epochs(lfp, onsets_ms, pre, post, fs)` | Returns `(n_trials, n_ch, T)` windowed array |

## lfp_tfr — full api
| Function | Purpose |
|---|---|
| `compute_tfr(epoch, fs, nperseg, noverlap)` | Hanning STFT TFR — 98% overlap default; returns `(freqs, times, power)` |
| `compute_multitaper_tfr(data, fs, nperseg, noverlap)` | Alias for `compute_tfr` (compatibility wrapper) |
| `get_band_power(freqs, power, band)` | Slices TFR to a named band (theta/alpha/beta/gamma) |
| `collapse_band_power(freqs, power, band)` | Mean across frequency axis for a band → `(trials, T)` |

## lfp_stats — full api
| Function | Purpose |
|---|---|
| `mean_sem(x, axis)` | Returns `(mean, sem)` tuple along axis |
| `cluster_permutation_test(x, y, n_perm)` | 2D cluster-based permutation; returns p-value mask |
| `compare_tiers(tier_a, tier_b)` | Rank-sum test between hierarchy tiers; returns p, stat |
| `summarize_by_area(results, areas)` | Aggregates per-unit results into area-level dict |

## lfp_connectivity — full api
| Function | Purpose |
|---|---|
| `compute_coherence(sig1, sig2, fs)` | Magnitude-squared coherence between two LFP channels |
| `compute_pairwise_coherence(sig_a, sig_b, fs)` | Alias for `compute_coherence` (compatibility) |
| `compute_granger(*args, **kwargs)` | Spectral Granger directionality placeholder (Step 11); uses `nitime.GrangerAnalyzer` |

## lfp_plotting — full api
| Function | Purpose |
|---|---|
| `_style(fig)` | Applies `plotly_white`, Arial, black axes to any figure |
| `create_tfr_figure(freqs, times_ms, power, title)` | TFR heatmap with full sequence event patches |
| `plot_tfr_grid(tfr_dict, areas)` | Grid of TFR heatmaps across areas |
| `create_band_plot(times_ms, mean_pwr, sem_pwr, title, color)` | Band trajectory with ±2SEM shading |
| `plot_band_trajectories(bands, times_ms, area)` | All 5 bands in subplots for one area |
| `plot_coherence_network(coh_matrix, areas, band)` | 11×11 heatmap of inter-area coherence |
