---
name: analysis-nwb-area-inspection
description: Provides a detailed inspection of Neurodata Without Borders (NWB) files to extract and display metadata related to session descriptions, electrode groups (probes), and recording devices. This skill is vital for understanding the experimental setup, particularly the physical arrangement and brain region assignments of recording probes.
---
# SKILL: analysis-nwb-area-inspection

## Description
This skill offers a deeper dive into the metadata contained within Neurodata Without Borders (NWB) files, focusing on the configuration of recording electrodes and devices. By parsing the NWB structure, it retrieves and displays crucial information such as the overall session description, detailed attributes of each electrode group (often corresponding to individual probes, including their location and description), and the specifications of the recording devices. This inspection is fundamental for verifying the experimental design, understanding the anatomical targeting of recordings, and ensuring the consistency of metadata across different NWB datasets.

## Core Tasks
1.  **Construct NWB Path**: Generates the full path to the NWB file based on a hardcoded session ID.
2.  **Load NWB File**: Opens and reads the specified NWB (`.nwb`) file using `NWBHDF5IO`.
3.  **Inspect Session Description**: Prints the `session_description` attribute of the NWB file.
4.  **Inspect Electrode Groups**: Iterates through `nwbfile.electrode_groups`, printing the name, description, location, and associated device for each group.
5.  **Inspect Devices**: Iterates through `nwbfile.devices`, printing details for each recording device.

## Inputs
*   **NWB File**: An NWB (`.nwb`) file (e.g., `data/nwb/sub-V198o_ses-230629_rec.nwb`). The `session_id` is hardcoded within the script.

## Outputs
*   **Console Output**: Displays a structured report including the session description, detailed information about each electrode group (probe), and an overview of the recording devices found in the NWB file.

## Example Use

```python
import os
import pynwb
from pynwb import NWBHDF5IO
from types import SimpleNamespace # For mocking NWB objects

# --- Mocking NWB data structures for demonstration ---
class MockDevice(SimpleNamespace):
    pass

class MockElectrodeGroup(SimpleNamespace):
    pass

class MockNWBFile(SimpleNamespace):
    def __init__(self, session_description, electrode_groups, devices):
        super().__init__(session_description=session_description)
        self.electrode_groups = electrode_groups
        self.devices = devices

class MockNWBHDF5IO:
    def __init__(self, path, mode, load_namespaces=True):
        self.path = path
        self.mode = mode

    def __enter__(self):
        # Simulate an NWB file with some metadata
        mock_device = MockDevice(name='ImplantA', description='Custom Probe Array')
        mock_group_v1 = MockElectrodeGroup(name='Probe_V1', description='V1 recording', location='V1', device=mock_device)
        mock_group_pfc = MockElectrodeGroup(name='Probe_PFC', description='PFC recording', location='PFC', device=mock_device)
        
        mock_nwbfile = MockNWBFile(
            session_description='Mock session for NWB area inspection',
            electrode_groups={'Probe_V1': mock_group_v1, 'Probe_PFC': mock_group_pfc},
            devices={'ImplantA': mock_device}
        )
        return mock_nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Mocking the inspect_nwb_file_deeper function ---
def mock_inspect_nwb_file_deeper(session_id):
    """
    Reads a mock NWB file and performs a deeper inspection of its metadata.
    """
    mock_nwb_file_path = f'data/nwb/sub-V198o_ses-{session_id}_rec.nwb' # Dummy path
    
    print(f"--- Deeper inspection of Mock NWB file: {mock_nwb_file_path} ---")

    try:
        with MockNWBHDF5IO(mock_nwb_file_path, 'r') as nwbfile:
            
            print("
--- Session Description ---")
            print(nwbfile.session_description)

            print("
--- Electrode Groups (Probes) Details ---")
            if not nwbfile.electrode_groups:
                print("No Electrode Groups found.")
            for group_name, group in nwbfile.electrode_groups.items():
                print(f"
Group Name: {group_name}")
                print(f"  Description: {group.description}")
                print(f"  Location: {group.location}")
                print(f"  Device: {group.device.name}")

            print("
--- Devices ---")
            if not nwbfile.devices:
                print("No Devices found.")
            for device_name, device in nwbfile.devices.items():
                 print(f"
Device Name: {device_name}")
                 print(device)
                 
    except Exception as e:
        print(f"
An error occurred while reading the NWB file: {e}")

# --- Run the demonstration ---
if __name__ == '__main__':
    session_to_inspect = '230629'
    mock_inspect_nwb_file_deeper(session_to_inspect)
```