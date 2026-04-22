---
name: analysis-lfp-pipeline
description: Modular LFP pipeline for sequential visual omission tasks. Covers NPY/NWB loading, TFR, connectivity, and Kaleido-Free Plotly standards.
---
# skill: analysis-lfp-pipeline

## When to Use
Use this skill for all Local Field Potential (LFP) analysis workflows. It is the primary reference for:
- Standardizing time-frequency representations (TFR).
- Calculating Spike-Field Coherence (SFC) and Phase Consistency.
- Generating cross-area connectivity matrices.
- Ensuring all plots adhere to the project's Madelane Golden Dark aesthetic and interactive HTML standards.

## What is Input
- **Raw Data**: Memory-mapped `.npy` arrays or NWB files.
- **Metadata**: Area-to-probe mappings (from `checkpoints/`).
- **Timing**: Event timestamps (p1 onset, omission onset).
- **Parameters**: Frequency ranges (2-100Hz), normalization windows (-1000 to 0ms).

## What is Output
- **TFR Arrays**: dB-normalized power heatmaps.
- **SFC Spectra**: Pairwise Phase Consistency (PPC) values across frequencies.
- **Figures**: Interactive Plotly HTML files (Fig 5-8).

## Algorithm / Methodology
1. **Normalization**: Applies dB change transformation ($10 \times \log_{10}(P/P_{baseline})$) relative to a fixation baseline.
2. **Spectral Analysis**: Uses Wavelet or Multi-taper transforms for time-frequency decomposition.
3. **Connectivity**: Computes power envelope correlations and phase-based metrics.
4. **Visual QA**: Ensures all figures include the native 'Download to SVG' button and follow color constraints.

## Placeholder Example
```python
from src.core.data_loader import DataLoader
from src.analysis.lfp_pipeline import LFPAnalyzer

# 1. Load data
loader = DataLoader()
lfp = loader.get_signal(mode="lfp", area="V1", session="230630")

# 2. Run TFR
analyzer = LFPAnalyzer(sampling_rate=1000)
tfr_db = analyzer.compute_tfr(lfp, baseline_win=(-1.0, 0.0))

# 3. Export figure
analyzer.plot_tfr(tfr_db, save_path="outputs/fig5_v1_tfr.html")
```

## Relevant Context / Files
- [src/core/data_loader.py](file:///D:/drive/omission/src/core/data_loader.py) — Data access.
- [src/analysis/lfp_pipeline.py](file:///D:/drive/omission/src/analysis/lfp_pipeline.py) — Core logic.
- [OmissionPlotter](file:///D:/drive/omission/src/utils/plotting.py) — Visualization.
