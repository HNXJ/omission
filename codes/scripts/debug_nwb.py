
import pandas as pd
from pynwb import NWBHDF5IO
import os

# Let's use one of the files that caused an error
NWB_PATH = 'data/sub-C31o_ses-230630_rec.nwb'

def inspect_nwb_units(nwb_path):
    """Inspects the structure of the units table in an NWB file."""
    if not os.path.exists(nwb_path):
        print(f"Error: NWB file not found at {nwb_path}")
        return

    print(f"Inspecting NWB file: {nwb_path}")
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            
            print("\n--- Units Table Info ---")
            units_df = nwbfile.units.to_dataframe()
            print("Columns available in units table:")
            print(units_df.columns)
            
            print("\nFirst 5 rows of units table:")
            print(units_df.head())

            print("\n--- Electrodes Table Info ---")
            electrodes_df = nwbfile.electrodes.to_dataframe()
            print("Columns available in electrodes table:")
            print(electrodes_df.columns)
            
            print("\nFirst 5 rows of electrodes table:")
            print(electrodes_df.head())


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Force pandas to display all columns
    pd.set_option('display.max_columns', None)
    inspect_nwb_units(NWB_PATH)
