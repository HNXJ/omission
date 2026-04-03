---
name: analysis-global-unit-counts-nwb
description: Audits Neurodata Without Borders (NWB) files to calculate and report the total number of recorded neural units assigned to predefined target brain areas across all sessions. This provides a global overview of the neural data coverage per brain region.
---
# SKILL: analysis-global-unit-counts-nwb

## Description
This skill provides a method to audit Neurodata Without Borders (NWB) files and calculate the global count of neural units per predefined target brain area across all available sessions. It processes NWB files, extracts unit and electrode information, maps units to specific brain regions based on their location, and then aggregates these counts to present a comprehensive overview of neural data coverage. This is essential for understanding the distribution of recorded units across the cortical hierarchy.

## Core Tasks
1.  **Scan NWB Files**: Identifies all NWB (`.nwb`) files within a specified data directory.
2.  **Extract Unit Metadata**: Reads unit and electrode metadata from each NWB file to determine unit locations.
3.  **Map Units to Areas**: Assigns each recorded unit to a specific brain area based on electrode mapping and predefined area definitions.
4.  **Aggregate Global Counts**: Sums the number of units per brain area across all processed NWB sessions.
5.  **Report Counts**: Prints the global unit counts for each target brain area to the console.

## Inputs
*   A directory containing NWB (`.nwb`) files (e.g., `data/`).

## Outputs
*   Console output displaying a formatted list of global unit counts per target brain area (e.g., V1, PFC, FEF) across all analyzed NWB sessions.

## Example Use

```python
import os
import pandas as pd
from pynwb import NWBHDF5IO
from collections import defaultdict
import numpy as np # For mocking unit['peak_channel_id'] as float then int

# --- Mocking NWB data structures for demonstration ---
class MockUnits:
    def __init__(self, units_data):
        self._units_data = units_data

    def to_dataframe(self):
        return pd.DataFrame(self._units_data)

class MockElectrodes:
    def __init__(self, electrodes_data):
        self._electrodes_data = electrodes_data

    def loc(self, idx):
        return self._electrodes_data[idx]

class MockNWBFile:
    def __init__(self, units_data, electrodes_data):
        self.units = MockUnits(units_data)
        self.electrodes = MockElectrodes(electrodes_data)

class MockNWBHDF5IO:
    def __init__(self, path, mode, load_namespaces=True):
        self.path = path
        self.mode = mode

    def __enter__(self):
        # Simulate NWB content for a session
        session_id = os.path.basename(self.path).split('_')[1].split('-')[1]
        
        # Mock units
        units_data = [
            {'peak_channel_id': 50.0}, {'peak_channel_id': 70.0}, {'peak_channel_id': 150.0},
            {'peak_channel_id': 200.0}, {'peak_channel_id': 300.0}
        ]
        
        # Mock electrodes
        electrodes_data = {
            50: {'location': 'V1'}, 70: {'location': 'V1'},
            150: {'location': 'PFC'}, 200: {'location': 'PFC'},
            300: {'location': 'MT'}
        }
        
        # Simulate multiple NWB files for glob.glob
        if "230630" in session_id:
            self.nwbfile = MockNWBFile(units_data[:2], electrodes_data) # V1
        elif "230816" in session_id:
            self.nwbfile = MockNWBFile(units_data[2:4], electrodes_data) # PFC
        else: # For other sessions
            self.nwbfile = MockNWBFile(units_data[4:], electrodes_data) # MT
            
        return self.nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Redefine the core function for demonstration ---
def demo_check_global_counts():
    print("--- Demonstrating NWB Global Unit Counts ---")
    
    # Simulate a few NWB files (they won't actually be read)
    mock_nwb_files = [
        'data/sub-monkey_ses-230630_rec.nwb',
        'data/sub-monkey_ses-230816_rec.nwb',
        'data/sub-monkey_ses-230830_rec.nwb'
    ]
    
    global_counts = defaultdict(int)

    # Simplified AREA_MAPPING and TARGET_AREAS for demo
    AREA_MAPPING = {'DP': 'V4'}
    TARGET_AREAS = ['V1', 'PFC', 'MT', 'V4']
    CHANNELS_PER_PROBE = 128
    
    for nwb_path in mock_nwb_files:
        print(f"  Processing mock NWB: {os.path.basename(nwb_path)}")
        try:
            # Use mock NWB reader
            with MockNWBHDF5IO(nwb_path, 'r') as io:
                nwbfile = io.nwbfile # Access the mock NWBFile instance
                
                if nwbfile.units is None or nwbfile.electrodes is None: continue
                
                units_df = nwbfile.units.to_dataframe()
                
                for idx, unit in units_df.iterrows():
                    peak_chan_id = int(float(unit['peak_channel_id']))
                    # In mock, directly get location from mocked electrodes
                    elec_loc = nwbfile.electrodes.loc(peak_chan_id)['location']
                    
                    if elec_loc in TARGET_AREAS: # Simple check for demo
                        global_counts[elec_loc] += 1
        except Exception as e:
            print(f"    Error processing mock NWB: {e}")
            continue

    print("
Global Unit Counts across ALL mock sessions:")
    for area in TARGET_AREAS:
        print(f"  - {area}: {global_counts[area]}")

# --- Run the demonstration ---
if __name__ == '__main__':
    demo_check_global_counts()
```