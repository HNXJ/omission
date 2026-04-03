---
name: analysis-mapping-debug
description: This skill provides debugging capabilities for the mapping of neural units to specific brain areas within Neurodata Without Borders (NWB) files. It helps verify the correctness of electrode-to-area assignments and the logic used to derive unit locations, which is critical for spatially resolved neural analyses.
---
# SKILL: analysis-mapping-debug

## Description
This skill is designed for debugging and validating the process of mapping recorded neural units to predefined brain areas, using data from Neurodata Without Borders (NWB) files. It specifically examines the logic that extracts electrode locations, applies an area mapping (e.g., from raw labels to standardized brain regions), and assigns units based on channel information. This is essential for ensuring that downstream analyses, which depend on accurate spatial localization of units, are built upon correctly mapped data. The skill provides print statements to trace the mapping process for individual units.

## Core Tasks
1.  **Load NWB Data**: Reads unit and electrode metadata from a specified NWB (`.nwb`) file.
2.  **Extract Unit and Electrode Info**: Retrieves the `peak_channel_id` for each unit and the `location` or `label` for each electrode.
3.  **Apply Area Mapping**: Translates raw electrode location labels into standardized brain area names using `AREA_MAPPING`.
4.  **Assign Units to Areas**: Based on probe ID, channel number within the probe, and the `AREA_MAPPING`, assigns each unit to a final brain area.
5.  **Debug Output**: Prints the unit index, peak channel ID, probe ID, and the assigned brain area to the console, allowing for step-by-step verification of the mapping logic.

## Inputs
*   **NWB File**: A specific NWB (`.nwb`) file (e.g., `data/nwb/sub-C31o_ses-230818_rec.nwb`) containing the unit and electrode metadata.

## Outputs
*   **Console Output**: Detailed debug messages for each unit, showing its index, peak channel, derived probe ID, and the final assigned brain area.

## Example Use

```python
import numpy as np
import pandas as pd
import os
from pynwb import NWBHDF5IO
from collections import defaultdict
import re
from types import SimpleNamespace # For mocking NWB objects

# --- Mocking constants from debug_mapping.py ---
AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128

# --- Mocking NWB data structures for demonstration ---
class MockUnitsDF:
    def __init__(self, units_data):
        self._units_data = units_data
    def iterrows(self):
        for i, row in enumerate(self._units_data):
            yield i, pd.Series(row)

class MockElectrodesDF:
    def __init__(self, electrodes_data):
        self._electrodes_data = electrodes_data
    def loc(self, idx):
        return pd.Series(self._electrodes_data.get(idx, {'location': 'unknown'}))

class MockNWBFile:
    def __init__(self, units_data, electrodes_data):
        self.units = MockUnitsDF(units_data)
        self.electrodes = MockElectrodesDF(electrodes_data)

class MockNWBHDF5IO:
    def __init__(self, path, mode, load_namespaces=True):
        self.path = path
        self.mode = mode

    def __enter__(self):
        # Simulate NWB content for a session
        # Unit data with peak channel IDs
        units_data = [
            {'peak_channel_id': 10.0},  # Probe 0, V1
            {'peak_channel_id': 130.0}, # Probe 1, PFC
            {'peak_channel_id': 200.0}  # Probe 1, V3d (mapped from V3)
        ]
        
        # Electrodes data
        electrodes_data = {
            10: {'location': 'V1'},
            130: {'location': 'PFC'},
            200: {'location': 'V3'} # Will be mapped to V3d, V3a
        }
        
        self.nwbfile = MockNWBFile(units_data, electrodes_data)
        return self.nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Redefine the core function for demonstration ---
def mock_debug_session_mapping():
    print("--- Demonstrating Session Mapping Debug (Mock) ---")
    
    # Mock NWB path (no actual file needed, just for context)
    mock_nwb_path = 'data/nwb/sub-C31o_ses-230818_rec.nwb'
    
    with MockNWBHDF5IO(mock_nwb_path, 'r') as io: # Use mock IO
        nwbfile = io.nwbfile
        units_df = nwbfile.units
        electrodes_df = nwbfile.electrodes
        
        print(f"  Debugging unit to area mapping for mock NWB: {mock_nwb_path}")
        
        for idx, unit in units_df.iterrows():
            peak_chan_id = int(float(unit['peak_channel_id']))
            elec = electrodes_df.loc(peak_chan_id)
            raw_label = elec.get('location', 'unknown') # Simplified get for mock
            if isinstance(raw_label, bytes): raw_label = raw_label.decode('utf-8')
            clean_label = raw_label.replace('/', ',')
            raw_areas = [a.strip() for a in clean_label.split(',')]
            mapped_areas = []
            for a in raw_areas:
                m = AREA_MAPPING.get(a, a)
                if isinstance(m, list): mapped_areas.extend(m)
                else: mapped_areas.append(m)
            
            num_areas = len(mapped_areas)
            channel_in_probe = peak_chan_id % CHANNELS_PER_PROBE
            segment_width = CHANNELS_PER_PROBE / num_areas if num_areas > 0 else 0
            
            assigned_area = "UNKNOWN"
            if num_areas > 0 and segment_width > 0:
                area_index = int(channel_in_probe // segment_width)
                area_index = min(area_index, num_areas - 1)
                assigned_area = mapped_areas[area_index]
            
            probe_id = int(peak_chan_id // CHANNELS_PER_PROBE)
            print(f"  DEBUG: Unit {idx}, PeakChan {peak_chan_id} -> Probe {probe_id}, Raw '{raw_label}', Assigned Area '{assigned_area}'")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_debug_session_mapping()
```