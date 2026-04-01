
import sys
import os
import glob
from collections import defaultdict
import pandas as pd
from pynwb import NWBHDF5IO

# Add the Jnwb directory to the Python path to allow imports
sys.path.append(os.path.abspath('Jnwb'))
import jnwb.core as jnwb_core

def list_all_areas():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    all_unique_areas = set()

    print(f"Checking {len(nwb_files)} NWB files for area labels...")

    for nwb_path in nwb_files:
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                if nwbfile.electrodes is not None:
                    df = nwbfile.electrodes.to_dataframe()
                    if 'location' in df.columns:
                        areas = df['location'].unique()
                        for a in areas:
                            val = a.decode('utf-8') if isinstance(a, bytes) else str(a)
                            all_unique_areas.add(val)
                    elif 'label' in df.columns:
                        areas = df['label'].unique()
                        for a in areas:
                            val = a.decode('utf-8') if isinstance(a, bytes) else str(a)
                            all_unique_areas.add(val)
        except Exception as e:
            print(f"Error reading {nwb_path}: {e}")

    print("\nAll unique area labels found across all sessions:")
    for a in sorted(list(all_unique_areas)):
        print(f"  - '{a}'")

if __name__ == '__main__':
    list_all_areas()
