---
name: analysis-metadata-extraction
description: Extracts comprehensive trial metadata from Neurodata Without Borders (NWB) files and saves it into a CSV format for easy tabular analysis. This skill is useful for quickly accessing and manipulating trial-specific information such as start/stop times, conditions, and behavioral events.
---
# SKILL: analysis-metadata-extraction

## Description
This skill facilitates the extraction of detailed trial metadata from Neurodata Without Borders (NWB) files. It targets the 'intervals' section within an NWB file, specifically looking for 'omission_glo_passive' or 'trials' tables. Once identified, it converts this structured data into a Pandas DataFrame and saves it as a CSV file. This CSV output provides an accessible, tabular format for researchers to inspect, filter, and perform preliminary analyses on trial-specific parameters without needing to interact directly with the NWB object structure.

## Core Tasks
1.  **Locate NWB File**: Takes a path to an NWB file and a session ID as command-line arguments.
2.  **Read NWB Intervals**: Opens the specified NWB file and accesses its 'intervals' module.
3.  **Identify Trial Table**: Prioritizes 'omission_glo_passive' table, falling back to 'trials' if the former is not found.
4.  **Convert to DataFrame**: Transforms the identified interval table into a Pandas DataFrame.
5.  **Save to CSV**: Exports the DataFrame to a CSV file named `ses-<session_id>_trials.csv` in a specified output directory. Includes a check to skip if the CSV already exists.

## Inputs
*   **`nwb_path`**: (Command-line argument) The full path to the NWB (`.nwb`) file from which to extract metadata.
*   **`session_id`**: (Command-line argument) A unique identifier for the session, used in the output CSV filename.

## Outputs
*   **`ses-<session_id>_trials.csv`**: A CSV file (e.g., `D:/hnxj-gemini/ses-230818_trials.csv`) containing the trial metadata. Each row represents a trial, and columns correspond to various trial parameters (start/stop times, conditions, etc.).

## Example Use

```python
import os
import sys
import pandas as pd
from pynwb import NWBHDF5IO
from datetime import datetime
from types import SimpleNamespace # For mocking NWB objects

# --- Mocking the extract_trial_metadata function and NWB structures ---
def mock_extract_trial_metadata(nwb_path, session_id, output_base_dir):
    output_path = os.path.join(output_base_dir, f'ses-{session_id}_trials.csv')
    
    if os.path.exists(output_path):
        print(f"  Mock metadata already exists for {session_id}. Skipping.")
        return
    
    print(f"  Mock: Opening {nwb_path}...")
    
    try:
        # Simulate NWB file structure
        # Create a dummy DataFrame for the trials table
        mock_trial_data = {
            'start_time': [0.0, 2.5, 5.0],
            'stop_time': [2.0, 4.5, 7.0],
            'task_condition_number': [1, 2, 1],
            'condition_name': ['A', 'B', 'A']
        }
        mock_df = pd.DataFrame(mock_trial_data)
        
        # Mocking the NWB object
        mock_intervals = SimpleNamespace(
            get=lambda name: mock_df if name == 'omission_glo_passive' else None
        )
        mock_nwb = SimpleNamespace(intervals=mock_intervals)
        
        # Simulate NWBHDF5IO
        class MockIO:
            def __enter__(self): return mock_nwb
            def __exit__(self, exc_type, exc_val, exc_tb): pass

        with MockIO() as nwb: # Use mock_nwb directly
            intervals = nwb.intervals
            target_table = intervals.get('omission_glo_passive') or intervals.get('trials')
            
            if target_table is not None: # Check if target_table was actually found
                df = target_table
                df.to_csv(output_path, index=False)
                print(f"  Mock: Saved {len(df)} trials to {output_path}")
            else:
                print("  Mock: No suitable interval table found.")
    except Exception as e:
        print(f"  Mock Error: {e}")

# --- Demonstration ---
if __name__ == "__main__":
    print("--- Demonstrating Metadata Extraction (Mock) ---")
    
    # Define a mock output directory
    mock_output_base_dir = "mock_output"
    os.makedirs(mock_output_base_dir, exist_ok=True)
    
    mock_nwb_path = "data/nwb/sub-C31o_ses-230818_rec.nwb" # Dummy path
    mock_session_id = "230818"
    
    # Run the mock extraction
    mock_extract_trial_metadata(mock_nwb_path, mock_session_id, mock_output_base_dir)
    
    # Verify the output (optional)
    generated_csv_path = os.path.join(mock_output_base_dir, f'ses-{mock_session_id}_trials.csv')
    if os.path.exists(generated_csv_path):
        print(f"
  Mock CSV content:
{pd.read_csv(generated_csv_path).to_markdown(index=False)}")
    
    # Clean up mock environment
    import shutil
    shutil.rmtree(mock_output_base_dir)
    print("
  Cleaned up mock environment.")

```