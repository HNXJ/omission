import pynwb
from pynwb import NWBHDF5IO
import os
import pandas as pd
from pathlib import Path

# NWB and Output
NWB_DIR = Path(r'D:\analysis\nwb')
OUTPUT_PATH = Path('outputs/unit_nwb_profile.csv')

def create_unit_profile():
    nwb_files = [f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')]
    all_profiles = []
    
    print("Building comprehensive unit_nwb_profile.csv with all NWB attributes...")
    
    for f in nwb_files:
        print(f'Processing {f}...')
        try:
            with NWBHDF5IO(str(NWB_DIR / f), 'r') as io:
                nwb = io.read()
                if nwb.units is not None:
                    # Get full unit metadata
                    unit_df = nwb.units.to_dataframe()
                    
                    # Electrode group/probe info
                    elec_df = nwb.electrodes.to_dataframe()
                    elec_df['elec_id'] = elec_df.index
                    
                    # Cast keys for safe merge
                    unit_df['peak_channel_id'] = pd.to_numeric(unit_df['peak_channel_id'], errors='coerce').fillna(-1).astype(int)
                    elec_df['elec_id'] = pd.to_numeric(elec_df['elec_id'], errors='coerce').fillna(-1).astype(int)
                    
                    # Merge electrode info
                    unit_profile = unit_df.merge(
                        elec_df[['elec_id', 'group_name', 'probe', 'location']], 
                        left_on='peak_channel_id', 
                        right_on='elec_id', 
                        how='left'
                    )
                    
                    # Add session and unit tracking
                    unit_profile['session_nwb'] = f
                    unit_profile['unit_id_in_session'] = unit_df.index
                    
                    # Keep all columns (dropping the redundant merge-key)
                    if 'elec_id' in unit_profile.columns:
                        unit_profile = unit_profile.drop(columns=['elec_id'])
                        
                    all_profiles.append(unit_profile)
                    
        except Exception as e:
            print(f'Error processing {f}: {e}')

    if all_profiles:
        master_df = pd.concat(all_profiles, ignore_index=True)
        master_df.to_csv(OUTPUT_PATH, index=False)
        print(f'Profile created with {len(master_df)} units and {master_df.shape[1]} columns.')
    else:
        print('No units found.')

if __name__ == "__main__":
    create_unit_profile()
