import pynwb
from pynwb import NWBHDF5IO
import os
import pandas as pd
from pathlib import Path

# Use the confirmed NWB directory
NWB_DIR = Path(r'D:\analysis\nwb')
OUTPUT_PATH = Path('outputs/all_units_metadata_v2.csv')

def extract_all_units():
    nwb_files = [f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')]
    all_unit_dfs = []
    
    for f in nwb_files:
        print(f'Processing {f}...')
        try:
            with NWBHDF5IO(str(NWB_DIR / f), 'r') as io:
                nwb = io.read()
                if nwb.units is not None:
                    df = nwb.units.to_dataframe()
                    # Add session and metadata markers
                    df['session_nwb'] = f
                    # Extract ID from filename if possible
                    all_unit_dfs.append(df)
        except Exception as e:
            print(f'Error processing {f}: {e}')

    if all_unit_dfs:
        master_df = pd.concat(all_unit_dfs, ignore_index=True)
        master_df.to_csv(OUTPUT_PATH, index=False)
        print(f'Master metadata created with {len(master_df)} units.')
        print(f'High-quality units (quality==1.0): {len(master_df[master_df["quality"] == 1.0])}')
    else:
        print('No units found.')

if __name__ == "__main__":
    extract_all_units()
