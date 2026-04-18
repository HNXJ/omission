---
name: analysis-omission-suite
description: Development standards and manuscript generation suite for the omission hierarchy project. Covers the 8-figure pipeline and Kaleido-Free standards.
---

# skill: analysis-omission-suite

## Canonical 8-Figure OGLO Pipeline
- **Fig 1: Theory**: Predictive Coding / Active Inference conceptual diagrams.
- **Fig 2: PSTH**: Trial-averaged firing rates (AAAB vs AXAB) for 11 areas.
- **Fig 3: Surprise**: Single-unit surprise latencies and prediction error magnitudes.
- **Fig 4: Coding**: Identity coding (A vs B) and population manifolds.
- **Fig 5: TFR**: Time-Frequency Spectrograms (dB relative power, 2-100Hz).
- **Fig 6: Bands**: 6-band power dynamics (Delta to High Gamma).
- **Fig 7: SFC**: Spike-Field Coupling (PPC) spectra for S+ and O+ neurons.
- **Fig 8: Harmony**: 11x11 Cross-Area Spectral coordination matrices.

## Development Standards
- **Entry Point**: `run_pipeline.py` at the workspace root.
- **Logic**: All figure generators must reside in `src/figures/` and use `src.core.plotting.OmissionPlotter`.
- **Aesthetic**: Madelane Golden Dark (#CFB87C / #9400D3).
- **Format**: Mandatory **Kaleido-Free** interactive HTML exports (`fig.write_html`).
- **Data**: Ingest from `D:/drive/data/arrays` using `DataLoader` with `mmap_mode='r'`.

## Manuscript (Figure-First Protocol)
- **Methods**: Transcribe from `methods-*.md` in `archive/` or `context/`.
- **Results**: Derived from the 8 generated figures in `D:/drive/outputs/oglo-8figs/`.
- **Target**: High-impact Neuroscience (e.g., Nature, Neuron).

## Execution Guardrails
- **Sanity**: Every figure script must print `[action]`, `[progress]`, and `[info]` logs.
- **Security**: Never log raw NWB paths or local credentials.
- **Root Hygiene**: No new files on root; only `run_pipeline.py` is permitted.
