---
name: analysis-summary-enrichment
---
# analysis-summary-enrichment

## Purpose
Appends NumPy array shape metadata (trials, channels, samples) to the data availability report. Verifies consistency of exported `.npy` dimensions.

## Input
| Name | Type | Description |
|------|------|-------------|
| summary_path | str | `DATA_AVAILABILITY_SUMMARY.md` |
| array_dir | str | `data/arrays/` containing `.npy` files |

## Output
| Name | Type | Description |
|------|------|-------------|
| enriched_md | str | Updated summary with "Detailed Array Shapes" table |

## Example
```python
from src.utils.reporting import enrich_data_summary
enrich_data_summary(summary_path="DATA_AVAILABILITY_SUMMARY.md")
print(f"""[result] Shape metadata appended""")
```

## Files
- [report_utils.py](file:///D:/drive/omission/src/extract/report_utils.py) — Implementation