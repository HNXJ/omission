---
name: analysis-area-inspection
---
# analysis-area-inspection

## Purpose
QC utility: inspects unique brain area labels in processed unit CSVs to catch nomenclature inconsistencies before batch analysis.

## Input
| Name | Type | Description |
|------|------|-------------|
| csv_path | str | Path to `checkpoints/omission_units_layered.csv` with an `area` column |

## Output
| Name | Type | Description |
|------|------|-------------|
| unique_areas | list[str] | All distinct area labels found |
| flagged_rows | DataFrame | Rows with compound labels (e.g. `V3/V4`) for manual audit |

## Example
```python
import pandas as pd
df = pd.read_csv('checkpoints/omission_units_layered.csv')
print(f"""[result] Unique areas: {df['area'].unique()}""")
print(f"""[flag] V3/V4 entries: {len(df[df['area'] == 'V3/V4'])}""")
```

## Files
- [omission_units_layered.csv](file:///D:/drive/omission/checkpoints/omission_units_layered.csv) — Primary data source