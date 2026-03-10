---
name: nwb-actions
description: Tool for creating, inspecting, and analyzing Neurodata Without Borders (NWB) files using PyNWB. Use when working with electrophysiology (LFP, Spikes, MUA) or behavioral data in neuroscience research.
---

# NWB Actions Skill

Guide for working with **Neurodata Without Borders** (NWB) files and **PyNWB**.

## Core Workflows

### 1. File Inspection
Quickly summarize the contents of an NWB file to check for Units, LFP, and Behavioral data.

**Workflow**:
- Run the inspection script: `python scripts/inspect_nwb.py <file.nwb>`
- Identify missing modules or misaligned timestamps.

### 2. Signal Definitions (LFP, MUA, Spikes)
When processing biological signals, ensure they are placed in the correct NWB containers:
- **LFP**: `processing/ecephys/LFP`
- **Spikes/Single Units**: `units` table (main top-level)
- **MUA**: `processing/ecephys/ElectricalSeries` (if integrated) or as unsorted units.
- **Behavior**: `processing/behavior/Position` or `Events`.

See [signals.md](references/signals.md) for a detailed breakdown of signal types and PyNWB objects.

### 3. Spectrolaminar Analysis (vFLIP2)
Use the `vFLIP2` class in `AAE/jnwb` to identify putative cortical layers based on the **spectrolaminar motif** (spectral crossover).

**Key Parameters**:
- `intdist`: Inter-channel distance (standard: 0.04 mm / 40um).
- `DataType`: Usually `raw_cut` for stimulus-aligned trial data.
- `orientation`: `both`, `upright`, or `inverted`.

**Motif Identification**:
- **Deep Layers**: Characterized by Alpha/Beta power peaks.
- **Superficial Layers**: Characterized by Gamma power peaks.
- **Layer 4**: Identified as the crossover point between these spectral profiles.

### 3. Creating NWB Files
When building a new NWB file, follow this order:
1. Initialize `NWBFile` with session metadata.
2. Define `Device` and `ElectrodeGroup`.
3. Map electrodes to `add_electrode`.
4. Append data via `add_unit`, `add_acquisition`, or `add_processing_module`.

## Key Resources

- `scripts/inspect_nwb.py`: Validation script for NWB structure.
- `references/signals.md`: Mapping of neuroscience signals to NWB objects.

## Usage Tips
- Always check the `session_start_time` for proper synchronization with external events.
- Prefer `NWBHDF5IO(path, 'r')` for inspection and `NWBHDF5IO(path, 'a')` for appending data.
- For behavioral synchronization, ensure all `SpatialSeries` share the same reference clock.
