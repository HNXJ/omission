---
name: lfp-core
description: Canonical LFP loading, area selection, TFR computation, and plotting guidance for the omission repo.
---

# SKILL: lfp-core

## Use this when
- you need omission-task LFP for a specific area from the 11-area hierarchy.
- you need p1-aligned epochs for plotting or spectral analysis.
- you want to reuse the repo’s canonical TFR functions or `OmissionPlotter`.

## Repo Truths
- **Time Axis**: Always relative to p1 onset (0ms). 
- **Canonical Areas**: V1, V2, V3d, V3a, V4, MT, MST, TEO, FST, FEF, PFC.
- **Storage**: Real arrays reside in `D:/drive/data/arrays/` as `ses{S}-probe{P}-lfp-{COND}.npy`.
- **Loading**: Use `mmap_mode='r'` in `DataLoader` to handle 100GB+ datasets without RAM overflow.

## Execution Steps
1. Instantiate `src.core.data_loader.DataLoader`.
2. Use `get_signal(mode="lfp", ...)` for area-specific extraction.
3. Apply **dB Normalization** using the -1000 to 0ms fixation window.
4. Generate **Kaleido-Free** interactive HTML figures via `OmissionPlotter`.

## Canonical Bands
- Delta: 1-4 Hz
- Theta: 4-8 Hz
- Alpha: 8-13 Hz
- Beta: 13-30 Hz
- Low Gamma: 35-55 Hz
- High Gamma: 65-100 Hz

## Minimal Example
```python
from src.core.data_loader import DataLoader
loader = DataLoader()
# Extracts list of (trials, channels, time) arrays for V1
v1_lfp_list = loader.get_signal(mode="lfp", condition="AXAB", area="V1")
```
