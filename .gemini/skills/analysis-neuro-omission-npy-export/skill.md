---
name: analysis-neuro-omission-npy-export
---
# analysis-neuro-omission-npy-export

## Purpose
Converts NWB sessions into chunked NumPy arrays (LFP, spikes, behavioral) with trial alignment and condition masking. Absorbs `analysis-npy-export`.

## Input
| Name | Type | Description |
|------|------|-------------|
| nwb_dir | str | Directory of `.nwb` session files |
| conditions | list[str] | Trial conditions (e.g. `['RRRR', 'RXRR']`) |
| window | tuple | Time range in s relative to p1 onset (default: -1.0 to +5.0) |

## Output
| Stream | Shape | dtype |
|--------|-------|-------|
| Behavioral | `(trials, 4, 6000)` | float32 |
| LFP/probe | `(trials, 128, 6000)` | float32 |
| Spikes/probe | `(trials, n_units, 6000)` | uint8 |

## Naming Convention
```
ses{id}-behavioral-{cond}.npy
ses{id}-probe{N}-lfp-{cond}.npy
ses{id}-units-probe{N}-spk-{cond}.npy
```

## Mandatory Rules
- Precompute `unit_indices_by_probe` once before trial loop
- `np.nan_to_num` on all loaded arrays
- `gc.collect()` after each condition
- Save `.metadata.json` sidecar with every batch

## Example
```python
from src.export.npy_pipeline import export_session_to_npy
export_session_to_npy('ses_001', {'window': (-1.0, 5.0), 'conditions': ['RRRR', 'RRXR']})
print(f"""[result] Exported to data/arrays/""")
```

## Files
- [npy_io.py](file:///D:/drive/omission/src/export/npy_io.py) — Block reading
- [npy_orchestrator.py](file:///D:/drive/omission/src/export/npy_orchestrator.py) — Main loop
