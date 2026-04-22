---
name: lfp-core
description: Canonical protocol for loading, selection, and spectral analysis of Local Field Potentials (LFP) in the Omission project.
---
# skill: lfp-core

## When to Use
Use this skill for all LFP-based analytical pipelines. It is mandatory for:
- Extracting area-specific signals from the 11-area cortical hierarchy (V1, PFC, etc.).
- Performing Time-Frequency Representations (TFR) using Wavelets or Multitapers.
- Aligning LFP epochs to stimulus onsets (Code 101.0).
- Calculating baseline-normalized power (dB) for Task-Related Potentials.

## What is Input
- **Raw Arrays**: `.npy` files located in `D:/drive/data/arrays/` (use `mmap_mode='r'`).
- **Metadata**: Condition labels (e.g., `AXAB`, `OMIT`), area identifiers, and channel indices.
- **Time Window**: Usually -500ms to +1000ms relative to target onset.

## What is Output
- **Condition Tensors**: `(trials, channels, time)` arrays for specific experiment blocks.
- **Power Spectra**: Interactive TFR heatmaps in HTML format.
- **Evoked Potentials**: Baseline-corrected (Z-scored or dB) LFP traces.

## Algorithm / Methodology
1. **Memory-Mapped Loading**: Enforces `mmap_mode='r'` to prevent system crashes when handling 100GB+ LFP datasets.
2. **Spectral Extraction**: Utilizes `scipy.signal.spectrogram` or `mne.time_frequency` for high-resolution power estimates.
3. **dB Normalization**: Power is calculated as `10 * log10(Signal / Baseline)`, where baseline is the -500 to 0ms fixation window.
4. **Band-Specific Filtering**: Standardizes on Delta (1-4Hz), Beta (13-30Hz), and Gamma (40-80Hz) for consistency with Predictive Routing theories.
5. **Channel Selection**: Automatically picks the "Best Channel" per area based on SNR or Signal Variance.

## Placeholder Example
```python
from src.core.data_loader import DataLoader

# 1. Initialize Loader with Memory Mapping
loader = DataLoader(mmap=True)

# 2. Extract Area-Specific LFP (trials, channels, time)
v1_lfp = loader.get_signal(mode="lfp", condition="AXAB", area="V1")

# 3. Compute TFR (using internal TFR engine)
tfr_data = compute_tfr(v1_lfp, fs=1000, freqs=np.arange(1, 100))
```

## Relevant Context / Files
- [math-neuro-omission-connectivity-metrics](file:///D:/drive/omission/.gemini/skills/math-neuro-omission-connectivity-metrics/skill.md) — For downstream coherence analysis.
- [src/core/data_loader.py](file:///D:/drive/omission/src/core/data_loader.py) — The canonical LFP extraction engine.
