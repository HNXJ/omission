---
name: analysis-nwb-teo-fst-channel-check
description: Inspects a specified Neurodata Without Borders (NWB) file to identify and list units that are located within the Temporo-occipital area (TEO) or the Fundus of the superior temporal sulcus (FST). This skill is used for targeted validation of unit assignments to these specific brain regions.
---
# SKILL: analysis-nwb-teo-fst-channel-check

## Description
This skill provides a focused inspection capability for Neurodata Without Borders (NWB) files, allowing for the identification and reporting of neural units located in specific brain regions: the Temporo-occipital area (TEO) and the Fundus of the superior temporal sulcus (FST). It is designed to quickly verify the presence and details of recordings from these areas within a given NWB dataset, serving as a targeted validation tool for experimental design or data quality checks.

## Core Tasks
1.  **Load NWB File**: Opens and reads a specified NWB (`.nwb`) file.
2.  **Access Unit and Electrode Metadata**: Extracts information about recorded units and their corresponding electrode locations.
3.  **Filter for TEO/FST Units**: Iterates through each unit, checks its `peak_channel_id`, and determines if the associated electrode's `location` or `label` contains "TEO" or "FST".
4.  **Report Units**: Prints a detailed list of identified TEO/FST units, including their index, probe ID, channel number, and raw electrode label.

## Inputs
*   `nwb_path`: The full path to a specific NWB (`.nwb`) file to be inspected.

## Outputs
*   Console output listing the units found within the TEO or FST regions, formatted with unit index, probe ID, channel, and the raw electrode label.

## Example Use

```python
import os
import pandas as pd
from pynwb import NWBHDF5IO
import numpy as np

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
        return pd.Series(self._electrodes_data[idx])

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
        # Units with peak channel IDs
        units_data = [
            {'peak_channel_id': 50.0}, {'peak_channel_id': 150.0}, # TEO/FST units
            {'peak_channel_id': 200.0}, {'peak_channel_id': 300.0}  # Other units
        ]
        
        # Electrodes data, ensuring 'location' contains TEO/FST for some channels
        electrodes_data = {
            50: {'location': 'TEO'},
            150: {'location': 'FST'},
            200: {'location': 'V1'},
            300: {'location': 'PFC'}
        }
        
        self.nwbfile = MockNWBFile(units_data, electrodes_data)
        return self.nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Redefine the core function for demonstration ---
def demo_check_teo_fst_channels(nwb_path):
    print(f"--- Demonstrating TEO/FST Channel Check for {os.path.basename(nwb_path)} ---")
    
    with MockNWBHDF5IO(nwb_path, 'r') as io:
        nwbfile = io.nwbfile
        units_df = nwbfile.units
        electrodes_df = nwbfile.electrodes
        
        print(f"Checking for TEO/FST units...")
        
        found_units = []
        for idx, unit in units_df.iterrows():
            peak_chan_id = int(float(unit['peak_channel_id']))
            elec = electrodes_df.loc(peak_chan_id)
            raw_label = elec.get('location', elec.get('label', 'unknown'))
            
            if "TEO" in raw_label or "FST" in raw_label:
                probe_id = peak_chan_id // 128 # Assuming 128 channels per probe
                channel_in_probe = peak_chan_id % 128
                found_units.append(f"Unit {idx}: Probe {probe_id}, Chan {channel_in_probe}, Label '{raw_label}'")
        
        if found_units:
            for u in found_units:
                print(u)
        else:
            print("  No TEO/FST units found in this mock file.")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_nwb_file = 'data/sub-C31o_ses-230818_rec.nwb' # Mocked path
    demo_check_teo_fst_channels(mock_nwb_file)
```