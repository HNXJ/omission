---
name: analysis-area-inspection
description: Provides a quick utility to inspect and verify the unique brain area labels present in a processed unit data CSV file and highlights specific entries for quality control. This skill is useful for ensuring consistency and correctness of brain region assignments before detailed analysis.
---
# SKILL: analysis-area-inspection

## Description
This skill offers a straightforward utility for quality control and verification of brain area assignments within processed neural unit data. It reads a specified CSV file containing unit information, extracts all unique labels from the 'area' column, and presents them to the user. Additionally, it highlights specific entries (e.g., those labeled 'V3/V4') to draw attention to potentially ambiguous or compound labels that might require further refinement or specific handling in subsequent analyses. This immediate feedback helps maintain data integrity and consistency in brain region categorization.

## Core Tasks
1.  **Load CSV Data**: Reads a Pandas DataFrame from the CSV file located at `checkpoints/omission_units_layered.csv`.
2.  **Extract Unique Areas**: Identifies and prints all unique values found in the 'area' column of the DataFrame.
3.  **Highlight Specific Entries**: Filters the DataFrame to show rows where the 'area' column matches a specific value (e.g., 'V3/V4') and prints the head of this filtered subset.

## Inputs
*   **`checkpoints/omission_units_layered.csv`**: A CSV file containing processed unit data, expected to have an 'area' column.

## Outputs
*   **Console Output**:
    *   A list of all unique brain area labels found in the 'area' column.
    *   The first few rows of the DataFrame where the 'area' column contains 'V3/V4'.

## Example Use

```python
import pandas as pd
import os

# --- Mocking the inspect_areas script functionality ---
def mock_inspect_areas():
    print("--- Demonstrating Area Inspection (Mock) ---")
    
    # Create a mock checkpoints directory
    os.makedirs('checkpoints', exist_ok=True)
    
    # Create a dummy omission_units_layered.csv file
    mock_data = {
        'unit_id': [1, 2, 3, 4, 5, 6],
        'session_id': [230629, 230629, 230630, 230630, 230701, 230701],
        'area': ['V1', 'PFC', 'V3/V4', 'TEO', 'V1', 'V3/V4'],
        'firing_rate': [10.5, 22.3, 5.1, 15.0, 11.2, 7.8]
    }
    mock_df = pd.DataFrame(mock_data)
    mock_csv_path = 'checkpoints/omission_units_layered.csv'
    mock_df.to_csv(mock_csv_path, index=False)
    
    print(f"  Mock CSV created at: {mock_csv_path}")

    # --- Replicate core logic of inspect_areas.py ---
    df = pd.read_csv(mock_csv_path)
    
    print("
  Unique values in 'area' column:")
    unique_areas = df['area'].unique()
    for area in unique_areas:
        print(f"  - {area}")

    print("
  Rows with 'V3/V4':")
    v3v4_rows = df[df['area'] == 'V3/V4']
    if not v3v4_rows.empty:
        print(v3v4_rows.head().to_markdown(index=False))
    else:
        print("  No rows found with 'V3/V4'.")

    # Clean up mock files (optional)
    os.remove(mock_csv_path)
    os.rmdir('checkpoints')
    print("
  Cleaned up mock environment.")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_inspect_areas()
```