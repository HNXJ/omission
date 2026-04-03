---
name: analysis-simultaneous-v1-pfc-check
description: Audits Neurodata Without Borders (NWB) files to identify sessions that contain simultaneous electrophysiological recordings from both the primary visual cortex (V1) and the prefrontal cortex (PFC). This skill is essential for filtering datasets suitable for V1-PFC connectivity or hierarchical analyses.
---
# SKILL: analysis-simultaneous-v1-pfc-check

## Description
This skill provides a method to audit Neurodata Without Borders (NWB) files to efficiently identify experimental sessions where simultaneous electrophysiological recordings were obtained from both the primary visual cortex (V1) and the prefrontal cortex (PFC). This identification is critical for downstream analyses focusing on inter-area connectivity, hierarchical processing, or communication-through-coherence between these two key brain regions in the context of omission paradigms.

## Core Tasks
1.  **Scan NWB Files**: Iterates through all `.nwb` files in a designated data directory.
2.  **Extract Electrode Metadata**: Reads electrode location metadata from each NWB file.
3.  **Map Areas**: Standardizes raw electrode location labels to recognized brain areas (e.g., V1, PFC).
4.  **Identify Simultaneous Recordings**: Checks if both V1 and PFC areas are represented in the recordings of a given NWB session.
5.  **Report Findings**: Outputs a summary indicating which sessions contain simultaneous V1 and PFC data.

## Inputs
*   A directory containing Neurodata Without Borders (`.nwb`) files.

## Outputs
*   Console output summarizing the brain areas found in each NWB session, with a clear indication for sessions that include simultaneous recordings from both V1 and PFC.

## Example Use

```python
import os
import pandas as pd
from pynwb import NWBHDF5IO
from collections import defaultdict
import numpy as np

# --- Mocking NWB data structures for demonstration ---
class MockElectrodesDF:
    def __init__(self, locations):
        self._locations = locations
    
    def get(self, key, default):
        if key == 'location':
            return np.array(self._locations, dtype=object) # Use numpy array of objects
        return np.array([default] * len(self._locations), dtype=object)

    def unique(self):
        return np.unique(self._locations)

class MockNWBFile:
    def __init__(self, electrodes_data):
        self.electrodes = type('Electrodes', (object,), {'to_dataframe': lambda self: pd.DataFrame(electrodes_data)})()
        self.electrodes.get = lambda key, default: MockElectrodesDF([d['location'] for d in electrodes_data]).get(key, default) # Mock get on electrodes

class MockNWBHDF5IO:
    def __init__(self, path, mode, load_namespaces=True):
        self.path = path
        self.mode = mode

    def __enter__(self):
        session_id = os.path.basename(self.path).split('_')[1].split('-')[0] # Simplified ID extraction
        
        if "ses-A" in session_id: # Session A has V1 and PFC
            electrodes_data = [{'location': 'V1'}, {'location': 'PFC'}, {'location': 'MT'}]
        elif "ses-B" in session_id: # Session B has only V1
            electrodes_data = [{'location': 'V1'}, {'location': 'V2'}]
        elif "ses-C" in session_id: # Session C has only PFC
            electrodes_data = [{'location': 'PFC'}, {'location': 'FEF'}]
        else:
            electrodes_data = [{'location': 'Unknown'}]

        self.nwbfile = MockNWBFile(electrodes_data)
        return self.nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Redefine the core function for demonstration ---
def demo_list_session_areas():
    print("--- Demonstrating Simultaneous V1-PFC Check ---")
    
    # Simulate a few NWB files (they won't actually be read by pynwb.NWBHDF5IO)
    mock_nwb_files = [
        'data/sub-monkey_ses-A_rec.nwb',
        'data/sub-monkey_ses-B_rec.nwb',
        'data/sub-monkey_ses-C_rec.nwb'
    ]
    
    session_areas = {}
    
    AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']} # Example mapping
    
    for nwb_path in mock_nwb_files:
        session_id = os.path.basename(nwb_path).split('ses-')[1].split('_')[0]
        print(f"  Processing mock NWB: {session_id}...")
        try:
            with MockNWBHDF5IO(nwb_path, 'r') as io:
                nwbfile = io.nwbfile
                if nwbfile.electrodes is None: continue
                
                # Mocking the unique method for electrode locations
                electrode_locations = [d['location'] for d in nwbfile.electrodes.to_dataframe().to_dict('records')]
                
                mapped_set = set()
                for raw_label in np.unique(electrode_locations): # Using np.unique to simulate unique
                    clean_label = str(raw_label).replace('/', ',')
                    areas = [a.strip() for a in clean_label.split(',')]
                    for a in areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped_set.update(m)
                        else: mapped_set.add(m)
                
                session_areas[session_id] = sorted(list(mapped_set))
        except Exception as e:
            print(f"    Error processing mock NWB: {e}")
            continue

    print("
--- Session-Area Availability ---")
    for ses, areas in session_areas.items():
        v1_pfc = "V1" in areas and "PFC" in areas
        status = "[V1+PFC!]" if v1_pfc else ""
        print(f"Ses {ses}: {', '.join(areas)} {status}")

# --- Run the demonstration ---
if __name__ == '__main__':
    demo_list_session_areas()
```