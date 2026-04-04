---
name: analysis-omission-suite
description: Development standards and manuscript generation suite for the omission hierarchy project. Covers figure pipeline architecture, NWB pipeline dev rules, and paper writing workflow.
---

# skill: analysis-omission-suite

## figure pipeline architecture (revision v4)
- **Fig02**: EYE_DVA — trial-averaged Eye-X/Y DVA, ±2SEM, pink omission patch (#FF1493, α=0.2).
- **Fig03**: SPK_AVG — grand average firing rates (Hz) for 11 canonical brain regions.
- **Fig04**: SPK_KMEANS — Group0=P1-responders (Gold) + Groups1-4 (k-means, k=4).
- **Fig05**: LFP_TFR — omission-position-specific TFR (X2: d1-p2-d2, X3: d2-p3-d3).
- **Fig06**: LFP_BANDS — pooled X2/X3 5-band traces + sorted dB-change bar plots.
- **Fig07**: LFP_SPK_CORR — Pearson's r (2–150Hz, 2Hz steps), spikes vs LFP power.
- **Fig08**: OM_EFFECT — neuron-by-neuron two-tailed t-test (p<0.01) matched stimulus pairs.

## development standards
- All scripts must reside in `codes/scripts/` (entrypoints) or `codes/functions/` (utilities).
- Save figures as both `.html` (interactive) and `.svg` (vector).
- Theme: `plotly_white`. Palette: Vanderbilt Gold `#CFB87C`, Electric Violet `#8F00FF`, Black `#000000`.
- Never save a figure if all values are NaN or 0 — log a task to `context/queue/` instead.
- Every derived `.npy` array must have a `.metadata.json` sidecar (provenance).

## manuscript (figure-first protocol)
- Methods: transcribe from `context/docs/` methodology files.
- Results: transcribe from figure manifest captions and observation notes.
- Stats: finalize p-values and significance markers before submission draft.
- Target: BioRxiv preprint (12p, 10f).

## nwb pipeline dev rules
- Alignment: always Code 101.0 = p1 onset = Sample 1000 = 0ms.
- Use `pynwb.NWBHDF5IO` for reads; always `load_namespaces=True`.
- Trial interval table key: `omission_glo_passive`.
