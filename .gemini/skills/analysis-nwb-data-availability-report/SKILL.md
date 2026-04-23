---
name: analysis-nwb-data-availability-report
---
# analysis-nwb-data-availability-report

## Purpose
Generates a data completeness matrix across all NWB sessions. Tracks presence of spikes, LFP, eye, and reward signals. Outputs the Stable-Plus exclusion list.

## Input
| Name | Type | Description |
|------|------|-------------|
| nwb_dir | str | Path to `.nwb` files |
| modality_tags | list[str] | Sensors to check (e.g. `['LFP', 'Spikes', 'Pupil']`) |

## Output
| Name | Type | Description |
|------|------|-------------|
| report_path | str | Path to `DATA_AVAILABILITY_SUMMARY.md` |
| yield_summary | dict | Total units/trials across valid sessions |

## Example
```python
from src.audit.availability import run_availability_audit
report = run_availability_audit("D:/drive/omission/data/nwb/")
print(f"""[result] Report saved to {report}""")
```

## Files
- [DATA_AVAILABILITY_SUMMARY.md](file:///D:/drive/omission/data/nwb/DATA_AVAILABILITY_SUMMARY.md) — Living document
- [availability.py](file:///D:/drive/omission/src/audit/availability.py) — Core audit