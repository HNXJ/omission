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
