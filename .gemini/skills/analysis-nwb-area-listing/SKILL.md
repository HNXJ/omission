---
name: analysis-nwb-area-listing
description: Scans all Neurodata Without Borders (NWB) files in the data directory to extract and list all unique brain area labels assigned to electrodes. This skill is useful for a quick overview of the anatomical coverage across an entire dataset and for validating naming conventions.
---
# SKILL: analysis-nwb-area-listing

## Description
This skill systematically navigates through all Neurodata Without Borders (NWB) files present in the `data/nwb` directory. For each file, it accesses the electrode table and extracts unique labels from either the 'location' or 'label' columns, which typically denote the brain region where each electrode is implanted. The primary purpose is to aggregate and present a consolidated, sorted list of all distinct brain area labels encountered across the entire experimental dataset. This provides a rapid and comprehensive overview of the anatomical scope of the recordings, helps in verifying consistency in electrode placement annotations, and can serve as an initial step for quality control in multi-session experiments.

## Core Tasks
1.  **Locate NWB Files**: Uses `glob` to find all NWB (`.nwb`) files within the `data/nwb` directory.
2.  **Iterate and Extract**: For each NWB file, it opens it using `NWBHDF5IO`, accesses the `electrodes` table, and extracts unique values from the 'location' column (or 'label' if 'location' is not present).
3.  **Aggregate Unique Areas**: Collects all unique area labels into a single set to ensure no duplicates.
4.  **Print Sorted List**: Sorts the collected unique area labels alphabetically and prints them to the console.

## Inputs
*   **NWB Files**: Located in `data/nwb/`. These files are expected to contain an `electrodes` table with 'location' or 'label' columns.
*   **Optional (Jnwb library)**: The script includes `sys.path.append(os.path.abspath('Jnwb'))` and `import jnwb.core as jnwb_core`, suggesting a dependency on a custom `Jnwb` library for NWB operations, though `jnwb_core` is not explicitly used in the `list_all_areas` function itself.

## Outputs
*   **Console Output**: A sorted list of all unique brain area labels found across all NWB files in the `data/nwb` directory.

## Example Use

```python
import os
import sys
import glob
from collections import defaultdict
import pandas as pd
from pynwb import NWBHDF5IO
from types import SimpleNamespace # For mocking NWB objects

# --- Mocking NWB data structures for demonstration ---
class MockElectrodesDF:
    def __init__(self, locations):
        self._df = pd.DataFrame({'location': locations})
    def to_dataframe(self):
        return self._df

class MockNWBFile(SimpleNamespace):
    def __init__(self, electrodes_data):
        super().__init__(electrodes=MockElectrodesDF(electrodes_data))

class MockNWBHDF5IO:
    def __init__(self, path, mode, load_namespaces=True):
        self.path = path
        self.mode = mode

    def __enter__(self):
        session_id = os.path.basename(self.path).split('_')[1].split('-')[1]
        
        # Simulate different electrode locations for different mock sessions
        if session_id == "230629":
            self.nwbfile = MockNWBFile(electrodes_data=['V1', 'PFC', 'TEO'])
        elif session_id == "230630":
            self.nwbfile = MockNWBFile(electrodes_data=['V1', 'V2', 'PFC', 'FST'])
        else:
            self.nwbfile = MockNWBFile(electrodes_data=['V4', 'MT'])
        return self.nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Mocking the list_all_areas function ---
def mock_list_all_areas():
    print("--- Demonstrating NWB Area Listing (Mock) ---")
    
    # Create mock NWB files (empty, just for glob to find them)
    os.makedirs('data/nwb', exist_ok=True)
    mock_nwb_filenames = [
        'data/nwb/sub-mock_ses-230629_rec.nwb',
        'data/nwb/sub-mock_ses-230630_rec.nwb',
        'data/nwb/sub-mock_ses-230701_rec.nwb'
    ]
    for fn in mock_nwb_filenames:
        with open(fn, 'w') as f: f.write("mock nwb content")

    mock_nwb_files = glob.glob('data/nwb/sub-*_ses-*_rec.nwb')
    all_unique_areas = set()

    print(f"  Checking {len(mock_nwb_files)} mock NWB files for area labels...")

    for nwb_path in mock_nwb_files:
        try:
            with MockNWBHDF5IO(nwb_path, 'r') as io:
                nwbfile = io.read()
                if nwbfile.electrodes is not None:
                    df = nwbfile.electrodes.to_dataframe()
                    if 'location' in df.columns:
                        areas = df['location'].unique()
                        for a in areas:
                            val = a.decode('utf-8') if isinstance(a, bytes) else str(a)
                            all_unique_areas.add(val)
                    # No 'label' check in mock for simplicity, assuming 'location'
        except Exception as e:
            print(f"  Error reading {nwb_path}: {e}")

    print("
  All unique area labels found across all mock sessions:")
    for a in sorted(list(all_unique_areas)):
        print(f"  - '{a}'")

    # Clean up mock environment
    import shutil
    shutil.rmtree('data/nwb')
    print("
  Cleaned up mock environment.")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_list_all_areas()
```