---
name: analysis-area-inspection
description: Provides a quick utility to inspect and verify the unique brain area labels present in a processed unit data CSV file and highlights specific entries for quality control. This skill is useful for ensuring consistency and correctness of brain region assignments before detailed analysis.
---
# skill: analysis-area-inspection

## When to Use
Use this skill for quality control and verification of brain area assignments within processed neural unit data. It is particularly useful before running large-scale analyses to ensure that region labels (e.g., 'V1', 'PFC') are consistent and to catch ambiguous or compound labels (e.g., 'V3/V4') that may require special handling or refinement.

## What is Input
- **`checkpoints/omission_units_layered.csv`**: A CSV file containing processed unit data. It MUST contain an 'area' column.

## What is Output
- **Console Output**:
    - A printed list of all unique brain area labels found in the 'area' column.
    - A preview (head) of rows labeled with specific regions of interest (e.g., 'V3/V4') for manual inspection.

## Algorithm / Methodology
1. **Load Data**: Reads the unit data CSV using Pandas.
2. **Identification**: Extracts unique values from the `area` column to identify the current nomenclature used in the dataset.
3. **Filtering**: Specifically targets potentially problematic or complex labels like 'V3/V4' by filtering the DataFrame.
4. **Presentation**: Displays results in the terminal for quick human auditing.

## Placeholder Example
```python
import pandas as pd

# 1. Load the checkpoint file
df = pd.read_csv('checkpoints/omission_units_layered.csv')

# 2. Inspect unique areas
print("Unique areas detected:")
print(df['area'].unique())

# 3. Check for specific area data quality
v3v4_preview = df[df['area'] == 'V3/V4'].head()
print("Preview of V3/V4 entries:")
print(v3v4_preview)
```

## Relevant Context / Files
- [checkpoints/omission_units_layered.csv](file:///D:/drive/omission/checkpoints/omission_units_layered.csv) — Primary data source for inspection.