import pynwb
from pynwb import NWBHDF5IO
import os
import pandas as pd
from pathlib import Path

# NWB and Output
NWB_DIR = Path(r'D:\analysis\nwb')
OUTPUT_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')

def create_unit_profile():
    nwb_files = [f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')]
    all_profiles = []
    
    print("Building comprehensive unit_nwb_profile.csv...")
    
    for f in nwb_files:
        print(f'Processing {f}...')
        try:
            with NWBHDF5IO(str(NWB_DIR / f), 'r') as io:
                nwb = io.read()
                if nwb.units is not None:
                    # Basic unit metadata
                    unit_df = nwb.units.to_dataframe()
                    
                    # Electrode group/probe info
                    elec_df = nwb.electrodes.to_dataframe()
                    elec_df['elec_id'] = elec_df.index
                    
                    # Map peak_channel_id -> Probe/Channel
                    # 'probe' is usually the device, 'group_name' is the probe name (e.g. ProbeA)
                    unit_df['peak_channel_id'] = pd.to_numeric(unit_df['peak_channel_id'], errors='coerce').fillna(-1).astype(int)
                    elec_df['elec_id'] = pd.to_numeric(elec_df['elec_id'], errors='coerce').fillna(-1).astype(int)
                    
                    # Merge to get Probe/Group mapping
                    # Column 'probe' has device info, 'group_name' has probe ID
                    unit_profile = unit_df.merge(
                        elec_df[['elec_id', 'group_name', 'probe']], 
                        left_on='peak_channel_id', 
                        right_on='elec_id', 
                        how='left'
                    )
                    
                    # Clean up and select columns
                    unit_profile['session_nwb'] = f
                    unit_profile['unit_id_in_session'] = unit_df.index
                    
                    # Select canonical profile columns
                    profile_cols = ['session_nwb', 'unit_id_in_session', 'peak_channel_id', 'group_name', 'probe', 'quality', 'firing_rate', 'snr']
                    all_profiles.append(unit_profile[profile_cols])
                    
        except Exception as e:
            print(f'Error processing {f}: {e}')

    if all_profiles:
        master_df = pd.concat(all_profiles, ignore_index=True)
        master_df.to_csv(OUTPUT_PATH, index=False)
        print(f'Profile created with {len(master_df)} units.')
    else:
        print('No units found.')

if __name__ == "__main__":
    create_unit_profile()
