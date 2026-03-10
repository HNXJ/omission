---
name: nwb-actions
description: Tool for creating, inspecting, and analyzing Neurodata Without Borders (NWB) files using PyNWB and the modular jnwb package. Focuses on electrophysiology (LFP, MUAe, Spikes) and spectrolaminar analysis.
---

# NWB Actions Skill

This skill guides the inspection, signal extraction, and spectrolaminar analysis of **NWB** files using the modular **`AAE.jnwb`** package.

## 1. Modular Package: `AAE.jnwb`
Always use the modular `jnwb` package for working with NWB data.
- **`jnwb.vflip2`**: `vFLIP2` class for spectrolaminar motif identification.
- **`jnwb.get_signal_array`**: Extract stimulus-aligned LFP, MUAe, Pupil, or Eye signals.
- **`jnwb.get_binary_events_for_code`**: Filter trial events by numeric codes.
- **`jnwb.get_unit_ids_for_area`**: Map single units to specific brain regions.
- **`jnwb.inspect_h5py_raw_structure`**: Low-level inspection using `h5py`.
- **`jnwb.reconstruct_nwb_inspected`**: Rebuild NWB files while verifying internal links.

## 2. Spectrolaminar Motif Analysis (vFLIP2)
Identify putative cortical layers using the spectral crossover between Deep and Superficial power profiles.

### Analysis Logic
- **Deep Layers (5/6)**: Characterized by Alpha/Beta power peaks (8-30Hz).
- **Superficial Layers (2/3)**: Characterized by Gamma power peaks (> 35Hz).
- **Layer 4 (Input)**: Pinpointed at the **crossover point** where high-frequency power begins to dominate.

### Parameters for Standard Probes
- `intdist`: **0.04 mm** (40um electrode spacing).
- `DataType`: `raw_cut` (aligned to stimulus onset).
- `orientation`: `both`.

## 3. Dataset Knowledge: Probe Mapping
Standard probe-to-region mappings for current datasets in `Analysis/nwb/nwbdata/`:

- **Session 230831**: probe_0 (FEF), probe_1 (MT/MST), probe_2 (V4/TEO).
- **Session 230901**: probe_0 (PFC), probe_1 (MT/MST), probe_2 (V3/V4).
- **Session 230720**: probe_0 (V1/V2), probe_1 (V3d/V3a).

## 4. Signal Extraction Patterns
- **Sampling Rate**: Always verify via timestamps; standard is **1000 Hz** for LFP and MUAe.
- **Trial Alignment**: 
  - Standard trigger: `task_event_2` (Stimulus Onset).
  - Window: 500ms pre-stimulus to 1000ms post-stimulus.
- **Storage**: Raw data is stored as continuous traces in `ElectricalSeries` objects.

### 4. Cross-Column Analysis Patterns
To mirror the "Modular Network Merging" biophysical logic, use multi-probe extraction:
- **Spatial Alignment**: Group electrodes by probe (e.g., `probe_0`, `probe_1`) and brain region (e.g., FEF, MT/MST).
- **Temporal Synchronization**: Use standard triggers (e.g., `task_event_2`) to align signals across distributed cortical columns.
- **Inter-Area Metrics**: Focus on cross-area coherence and phase-lag synchronization to study propagation of E/I dysfunction between V1 and PFC.

### 5. Signal Normalization & Variability
For continuous signals (MUAe, LFP Envelopes), use baseline Z-scoring and quantify cross-trial quenching.

**MUAe Z-Scoring**:
```python
import numpy as np
def zscore_signal(data, baseline_indices):
    baseline = data[baseline_indices[0]:baseline_indices[1]]
    return (data - np.mean(baseline)) / (np.std(baseline) + 1e-6)
```

**Variance Quenching**:
Neural variability (across trials) typically drops upon stimulus onset.
- **Metric**: `np.var(trial_stack, axis=0)` where `trial_stack` is `(Num_Trials, Timepoints)`.

## 6. Usage Guidelines
- **Task Reference**: See [Global Omission Task](./references/global_omission_task.md) for sequence logic and event codes.
- **Memory Efficiency**: Large NWB files (>100GB) should be accessed using `h5py` for targeted dataset slicing to avoid memory overflow.
