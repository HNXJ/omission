---
name: analysis-poster-figure-pipeline
description: End-to-end data preparation pipeline to build the inputs for poster_figures.py. Covers: loading, bipolar-ref, baseline normalization, band-power extraction, trial sorting, unit classification, and inter-area correlation computation.
cross-ref: analysis-poster-figures (figure rendering)
---

# skill: analysis-poster-figure-pipeline

## pipeline — band power hierarchy (main LFP figure)

```
NWB → load_session → extract_epochs (pre=1000ms, post=4200ms)
    → apply_bipolar_ref
    → baseline_normalize (window -500 to 0ms)
    → compute_tfr (nperseg=256, noverlap=251, hann)
    → get_band_power (band='Beta', freqs 15–25Hz)
    → collapse_band_power → mean_sem(axis=0)
    → {cond: {area: {'Beta': (mean, sem)}}}
    → plot_band_power_hierarchy(...)
```

### code template
```python
from codes.functions.lfp_io       import load_session
from codes.functions.lfp_preproc  import apply_bipolar_ref, baseline_normalize, extract_epochs
from codes.functions.lfp_tfr      import compute_tfr, get_band_power, collapse_band_power
from codes.functions.lfp_stats    import mean_sem
from codes.functions.poster_figures import plot_band_power_hierarchy, AREA_ORDER

traces, sems = {}, {}
for cond in ['RRRR','RXRR','RRXR','RRRX']:
    traces[cond], sems[cond] = {}, {}
    for area in AREA_ORDER:
        epochs = extract_epochs(lfp[area], onsets_ms, pre=1000, post=4200)
        normed = baseline_normalize(apply_bipolar_ref(epochs), (-500, 0))
        freqs, times, pwr = compute_tfr(normed, fs=1000)
        band_pwr = collapse_band_power(freqs, pwr, band=(15, 25))
        m, s = mean_sem(band_pwr, axis=0)
        traces[cond][area] = {'Beta': m}
        sems[cond][area]   = {'Beta': s}
```

## pipeline — spectral correlation matrices
```
band_power per trial per area (mean in window)
→ np.corrcoef(stacked_area_vectors)  # (n_areas, n_areas)
→ compute separately for stimulus window [0, 531ms]
  and omission window [531, 1562ms] (or per-position)
→ plot_spectral_corr_matrices(corr_stim, corr_omit)
```

## pipeline — neuron group classification (Poster 02)
```
extract_unit_traces(session_id, conds) → {unit_id: array(n_times)}
baseline_correct(traces)
t-test vs baseline per unit → p < 0.01 threshold
  Excited:  mean(stim_window) >> mean(baseline)
  Inhibited: mean(stim_window) << mean(baseline)
t-test omission window vs delay → p < 0.01
  Omission-selective: significant increase in omission window only
→ plot_neuron_group_traces / plot_omission_fraction_bars
```

## pipeline — spectral network graph
```
compute_coherence(lfp_a, lfp_b, fs=1000)  # per area pair per band
→ adj_matrix (n_areas, n_areas)
→ separately for stimulus window and omission window
→ plot_spectral_network(adj_matrix, band_label='Beta')   # omission
→ plot_spectral_network(adj_matrix, band_label='Gamma')  # stimulus
```

## mandatory checks before any figure
1. `np.nan_to_num` on all LFP arrays.
2. Verify n_trials ≥ 10 per condition per session.
3. Log sessions with missing areas to `context/queue/task-queue.md`.
4. If all values are NaN or zero → **do not save** the figure.
