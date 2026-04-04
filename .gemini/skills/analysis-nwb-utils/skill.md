---
name: analysis-nwb-utils
description: Utility and admin functions for NWB data management, session summary updates, timing validation, photodiode alignment, and data file organization.
---

# skill: analysis-nwb-utils

## session summary & metadata
| Function | File | Purpose |
|---|---|---|
| `get_session_id(filename)` | `update_data_summary.py` | Extracts session ID (e.g. '230629') from any filename pattern |
| `update_summary()` | `update_data_summary.py` | Rebuilds session-level summary CSV from all available .npy arrays |
| `update_summary_table()` | `update_summary.py` | Updates the master markdown/CSV summary table in `data/` |
| `organize_data_files(root)` | `organize_d_drive.py` | Moves/renames raw data files on D-drive to standardized directory layout |

## timing validation
| Function | File | Purpose |
|---|---|---|
| `plot_verification()` | `verify_timing.py` | Plots Code-101 alignment + V1 latency check for a single session |
| `plot_multi_v1(sessions)` | `verify_timing_multi.py` | Multi-session timing validation; V1 peak should appear 40–60ms post-photodiode |

## photodiode alignment
| Function | File | Purpose |
|---|---|---|
| `extract_photodiode()` | `photodiode_alignment.py` | Extracts photodiode channel from raw .nwb; detects rising edges as stimulus onsets |
| `plot()` | `photodiode_alignment.py` | Visualizes photodiode trace + detected onsets vs. behavorial codes |

## npy export orchestration
| Function | File | Purpose |
|---|---|---|
| `export_session_granular(nwb_path, session_id)` | `master_npy_export.py` | Full chunked export: NWB → behavioral/LFP/spike .npy arrays per condition |

## validation rules
- V1 firing rate peak must occur 40–60ms after photodiode onset — use `plot_verification` per session.
- Photodiode stays flat during omissions (luminance-matched background) — any change is a bug.
- After `export_session_granular`, verify array shapes: behavioral `(n_trials, 4, 6000)`, LFP `(n_trials, 128, 6000)`.
- `update_summary` must be run after each new export batch.

## internal tooling (low priority)
| Function | File | Purpose |
|---|---|---|
| `estimate_tokens(text)` | `qwen_subagent.py` | ~4 chars/token estimator for prompt budgeting |
| `call_qwen(prompt, system_prompt)` | `qwen_subagent.py` | Sends inference request to Office M3-Max via remote bridge |
| `manage_model(action, model_name)` | `qwen_subagent.py` | Load/unload model on remote server via API |

## lfp extraction testing
| Function | File | Purpose |
|---|---|---|
| `get_data_from_ref(nwb, ref_time, pre_ms, post_ms)` | `test_lfp_extraction.py` | Extracts a trial-aligned LFP window given a reference event time; used for debugging alignment |
