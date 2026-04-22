---
name: nwb-analysis
description: Unified data pipeline for NWB-based neurophysiology analysis, featuring manifold extraction, variability (MMFF), and hierarchical connectivity.
---
# skill: nwb-analysis

## When to Use
Use this skill for the primary data processing pipeline of the Omission project. It is mandatory for:
- Aligning spike trains and LFP signals to experimental events (P1, Omission onset).
- Calculating Mean-Matched Fano Factor (MMFF) using the Churchland 2010 protocol.
- Extracting 48-factor manifold matrices (12 intervals $\times$ 4 metrics) for population decoding.
- Applying probe-local mapping rules (128-channel rule, V3a/V3d splitting).
- Handling NWB lazy-loading context bugs using stable `h5py` access patterns.

## What is Input
- **NWB Files**: Raw or processed Neurodata Without Borders containers.
- **Timing Codes**: Event markers (e.g., Code 101.0 for P1 onset).
- **Processing Config**: Window sizes (100ms), step sizes (5ms), and smoothing kernels $(\sigma=50ms)$.

## What is Output
- **Time-Aligned Tensors**: 3D arrays (Trials $\times$ Neurons $\times$ Time) for firing rates and Fano Factors.
- **Manifold Vectors**: Flattened feature matrices for PCA/UMAP dimensionality reduction.
- **Categorization Labels**: Functional groups (O+, Stim+, Fixation-selective) assigned per unit.

## Algorithm / Methodology
1. **Alignment Logic**: Hard-aligned to P1 onset (1000ms after fixation start).
2. **Mean-Matched Fano Factor (MMFF)**: 
   - Window ($W=100$ms), Step ($\Delta t=5$ms).
   - Mean-matching performed across all conditions to decouple firing rate from variability.
3. **Probe Partitioning**: 
   - Uses `probe_id = peak_channel_id // 128`.
   - Area **DP** maps to **V4**; **V3** splits 50/50 into **V3d** and **V3a**.
4. **Stable Loading**: Uses `mmap_mode='r'` for large `.npy` exports and explicit `.close()` calls for NWB handles.

## Placeholder Example
```python
# 1. Align Data to Omission Window
# Window p2 (RXRR): 2031-2562ms post-P1
aligned_spikes = nwb_loader.get_aligned_window(event='p2', pre_ms=500, post_ms=1000)

# 2. Compute Smoothed Fano Factor
# Protocol: Sigma=2 Gaussian on final trace
ff_trace = mmff.compute(aligned_spikes, window=100, step=5)
smoothed_ff = gaussian_filter1d(ff_trace, sigma=2)
```

## Relevant Context / Files
- [lfp-core](file:///D:/drive/omission/.gemini/skills/lfp-core/skill.md) — For complementary LFP-based analysis.
- [src/data/nwb_loader.py](file:///D:/drive/omission/src/data/nwb_loader.py) — The canonical loader for all NWB assets.
