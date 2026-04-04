---
name: analysis-npy-export-io
description: I/O layer for the master NPY export pipeline. Handles NWB reading, trial masking, and chunked block extraction of LFP, behavioral, and spike data.
cross-ref: analysis-npy-export-pipeline (orchestration and save logic)
---

# skill: analysis-npy-export-io

## purpose
Reads raw NWB files and extracts windowed data blocks efficiently into memory for downstream export.

## core functions

### `get_oglo_trial_masks(trials_df)`
- **Source**: `jnwb.oglo_v2.get_oglo_trial_masks_v2` (external).
- Returns dict of condition → boolean trial mask.
- Conditions: RRRR, RXRR, RRXR, RRRX (and A/B variants).

### `get_block(acquisition_obj, t_start, t_end)`
- Extracts a time-windowed block from any NWB acquisition object.
- Returns `(block_data, rate, t0)`.
- Handles LFP (128ch), eye (2ch), pupil (1ch), reward (1ch).

### `preload_spike_times(nwb_units, n_units)`
- Pre-loads all spike times once per session to avoid repeated NWB reads.
- Returns `list[np.ndarray]` indexed by unit.

## alignment & window
- **Reference**: Code 101.0 = p1 onset.
- **Window**: 1000ms pre + 5000ms post p1 = 6000 samples at 1kHz.
- **Chunk size**: `TRIAL_CHUNK_SIZE` (default 32) trials per memory block.

## inputs
- `data/nwb/*.nwb` — NWB session files.
- `jnwb` library on Python path for trial masking.

## array shapes (per condition)
| Stream | Shape | dtype |
|---|---|---|
| Behavioral | `(n_trials, 4, 6000)` | float32 |
| LFP (per probe) | `(n_trials, 128, 6000)` | float32 |
| Spikes (per probe) | `(n_trials, n_units, 6000)` | uint8 |


---

---
name: analysis-npy-export-pipeline
description: Orchestration and save layer for the master NPY export. Iterates sessions and conditions, calls the IO layer, and writes named .npy files with metadata sidecars.
cross-ref: analysis-npy-export-io (block reading and trial masking)
---

# skill: analysis-npy-export-pipeline

## purpose
Orchestrates the full export loop: session → condition → chunked extraction → save.

## naming convention
```
ses{session_id}-behavioral-{cond}.npy
ses{session_id}-probe{id}-lfp-{cond}.npy
ses{session_id}-units-probe{id}-spk-{cond}.npy
```
All saved to `data/arrays/`.

## pipeline steps
1. Glob `data/nwb/*.nwb` → list of session paths.
2. Open NWB, extract `omission_glo_passive` intervals table.
3. Call `get_oglo_trial_masks` for condition split.
4. Find p1 onsets (Code 101.0) per trial.
5. Pre-load spike times for all units.
6. For each condition: allocate output arrays (float32/uint8).
7. Chunked loop (`TRIAL_CHUNK_SIZE`): call `get_block`, `slice_from_block`.
8. Save `.npy` arrays + `.metadata.json` sidecar (session, condition, shape, date).
9. `gc.collect()` after each condition.

## unit → probe mapping
```python
unit_probe_map = [int(float(nwb.units['peak_channel_id'][i])) // 128 for i in range(n_units)]
```

## mandatory
- `np.nan_to_num` on all loaded arrays.
- Verify output shape before save — skip and log if empty.
- `gc.collect()` after each chunked block.
