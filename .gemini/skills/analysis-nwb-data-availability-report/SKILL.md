---
name: analysis-nwb-data-availability-report
description: Generates a comprehensive Markdown summary table detailing the availability of various data modalities (spikes, LFP, eye, pupil, reward, trials, conditions) within NWB (.nwb) files for each session. This is crucial for auditing data completeness and guiding subsequent analysis.
---
# SKILL: analysis-nwb-data-availability-report

## Description
This skill provides a systematic method to audit and report on the contents of Neurodata Without Borders (NWB) files. It generates a comprehensive Markdown summary table that details the availability of various data modalities (such as spikes, LFP, eye tracking, pupillometry, and reward signals) within `.nwb` files for each recorded session. This report is crucial for quickly assessing data completeness and consistency across sessions, which in turn guides subsequent analysis pipelines.

## Core Tasks
1.  **Iterate NWB Files**: Scans a specified directory for all `.nwb` files.
2.  **Read NWB Contents**: Opens each `.nwb` file to inspect its contents.
3.  **Check Modality Availability**: Determines the presence and quantity of key neurophysiological and behavioral data streams (units/spikes, LFP, eye movements, pupil diameter, reward events).
4.  **Summarize Data**: Compiles the availability information for each session into a structured format.
5.  **Generate Markdown Report**: Creates a Markdown table from the summary data and saves it to a file.

## Inputs
*   A directory path (`NWB_DIR`) containing Neurodata Without Borders (`.nwb`) files.

## Outputs
*   A Markdown file named `DATA_AVAILABILITY_SUMMARY.md` located in the `NWB_DIR`. This file contains a table with columns for "Session", "Trials", "Conditions", "Units (SPK)", "LFP", "Eye (x,y)", "Pupil", and "Reward", indicating data presence for each NWB file.

## Example Use

```python
import os
import pandas as pd
from pynwb import NWBHDF5IO
import numpy as np

# Assuming check_availability.py is available or its functions are defined here.
# For a full example, you would need the original check_availability.py content
# or to mock its core logic.

# --- Mocking check_data_availability function for demonstration ---
def mock_check_data_availability(nwb_dir_path):
    print(f"Simulating data availability check in {nwb_dir_path}...")
    # In a real scenario, this would read actual NWB files.
    # Here, we create a dummy dataframe.
    availability_data = [
        {"Session": "230629", "Trials": 100, "Conditions": 4, "Units (SPK)": 50, "LFP": "Yes", "Eye (x,y)": "Yes", "Pupil": "No", "Reward": "Yes"},
        {"Session": "230630", "Trials": 120, "Conditions": 4, "Units (SPK)": 75, "LFP": "Yes", "Eye (x,y)": "Yes", "Pupil": "Yes", "Reward": "Yes"},
        {"Session": "230701", "Trials": 80, "Conditions": 3, "Units (SPK)": 0, "LFP": "No", "Eye (x,y)": "No", "Pupil": "No", "Reward": "No"}
    ]
    df = pd.DataFrame(availability_data)
    md_table = df.to_markdown(index=False)
    
    output_path = os.path.join(nwb_dir_path, 'DATA_AVAILABILITY_SUMMARY.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📊 Data Availability Summary (Mock Data)

")
        f.write(md_table)
    
    print(f"
--- Generated Mock Summary ---")
    print(md_table)
    print(f"
Summary table saved to {output_path}")

# --- Demonstration ---
# Define a mock NWB directory for output
mock_nwb_dir = "D:/Analysis/Omission/local-workspace/mock_nwb_data"
os.makedirs(mock_nwb_dir, exist_ok=True) # Ensure it exists for output

print("--- Demonstrating NWB Data Availability Report ---")

# Execute the mock function
mock_check_data_availability(mock_nwb_dir)

# Cleanup mock directory if desired
# shutil.rmtree(mock_nwb_dir)
```