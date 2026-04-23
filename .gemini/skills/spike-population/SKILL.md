---
name: spike-population
---
# spike-population

## Purpose
Population-level spiking dynamics: unit extraction, firing rate traces, Fano factor trajectories, and validated V1-PFC unit assignments.

## Input
| Name | Type | Description |
|------|------|-------------|
| session_id | str | Canonical date |
| areas | list[str] | Target cortical areas |

## Output
| Name | Type | Description |
|------|------|-------------|
| fr_traces | ndarray(units, T) | Population-averaged firing rates |
| unit_map | dict | Validated area assignments |

## Mandatory Rules
- Import from `src/analysis/spiking/*`, NOT legacy `codes/functions/spiking/`
- Output arrays must follow hierarchical area order (V1→PFC)

## Example
```python
from src.analysis.spiking.utils import extract_unit_traces
traces = extract_unit_traces(session_id="230629")
print(f"""[result] Trace shape: {traces.shape}""")
```

## Files
- [src/analysis/spiking/*](file:///D:/drive/omission/src/analysis/spiking/) — Core algorithms
