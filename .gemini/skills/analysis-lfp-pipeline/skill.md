---
name: analysis-lfp-pipeline
description: Modular LFP pipeline for sequential visual omission tasks. Covers NPY/NWB loading, TFR, connectivity, and Kaleido-Free Plotly standards.
---

# skill: analysis-lfp-pipeline

## Architecture (src/)
- **Data Loading**: Use `src.core.data_loader.DataLoader`. Supports memory-mapped `.npy` arrays for large session data.
- **Timing**: Canonical p1-onset at 0ms (Sample 1000). 
- **Preprocessing**: Baseline normalization (dB change) using -1000ms to 0ms fixation window.
- **TFR**: Log-spaced frequencies (2–100Hz), ms x-axis, dB relative power.
- **Connectivity**: 11x11 Cross-area power envelope correlations (Spectral Harmony).
- **SFC**: Pairwise Phase Consistency (PPC) across the full 1-100Hz spectrum.
- **Plotting**: Standardized `OmissionPlotter` for Kaleido-Free interactive HTML.

## Standards
- **Timing**: p1 = 0ms. p2 (Omission) = 1031ms.
- **Normalization**: dB change — $10 \times \log_{10}(P/P_{baseline})$ vs. fixation window (-1000 to 0ms).
- **Bands**: Delta (1-4Hz), Theta (4-8Hz), Alpha (8-13Hz), Beta (13-30Hz), Low-γ (35-55Hz), High-γ (65-100Hz).
- **Plotting**: Madelane Golden Dark (#CFB87C / #9400D3). Interactive HTML ONLY.

## Execution Rules
1. **Memory Efficiency**: Use `mmap_mode='r'` when loading `.npy` arrays from `D:/drive/data/arrays`.
2. **Deterministic Mapping**: Rely on `session-area-mapping.md` for probe-to-area assignment.
3. **PPC over Coherence**: Prefer PPC for SFC to avoid firing-rate bias.

## Figures Catalog
- **Fig 5**: TFR Heatmaps (dB normalized).
- **Fig 6**: Band Power Trajectories (6 bands, ±SEM).
- **Fig 7**: SFC PPC Spectra (S+ vs O+ ground truth).
- **Fig 8**: Cross-Area Spectral Harmony (11x11 Matrices).

## Quick Start
```python
from src.core.data_loader import DataLoader
loader = DataLoader()
lfp = loader.get_signal(mode="lfp", condition="AXAB", area="V1")
```
