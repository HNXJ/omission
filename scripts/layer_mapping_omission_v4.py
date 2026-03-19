
"""
layer_mapping_omission_v4.py: Maps identified omission neurons to cortical layers (Superficial, L4, Deep)
using the IMPROVED vFLIP2 mapping results (v3 CSV).
Uses the latest real_omission_units_layered_v3.csv and vflip2_mapping_v3.csv.
"""
import os
import pandas as pd
import numpy as np
from pynwb import NWBHDF5IO

# Paths
INPUT_UNITS_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/real_omission_units_layered_v3.csv'
VFLIP_CSV_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/vflip2_mapping_v3.csv'
NWB_DIR = 'D:/Analysis/Omission/local-workspace/data'
OUTPUT_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/real_omission_units_layered_v3.csv' # Updating the same file

def map_layers():
    if not os.path.exists(INPUT_UNITS_PATH):
        print(f"Error: Input units file not found at {INPUT_UNITS_PATH}")
        return
        
    df_units = pd.read_csv(INPUT_UNITS_PATH)
    if not os.path.exists(VFLIP_CSV_PATH):
        print(f"Error: Improved vFLIP mapping not found at {VFLIP_CSV_PATH}")
        return
        
    df_vflip = pd.read_csv(VFLIP_CSV_PATH)
    # Create mapping: (session_id, probe_id) -> crossover
    vflip_map = {}
    for _, row in df_vflip.iterrows():
        sid = str(row['session_id'])
        pid = str(row['probe_id'])
        vflip_map[(sid, pid)] = row['crossover']
    
    print(f"Loaded {len(vflip_map)} crossover mappings from improved vFLIP2.")
    
    # Layer mapping parameters
    BUFFER = 5 # L4 +/- 5 channels
    
    # Ensure session_id and probe_id in df_units are strings for matching
    df_units['session_id'] = df_units['session_id'].astype(str)
    df_units['probe_id'] = df_units['probe_id'].astype(str)
    
    # Track statistics
    counts = {'mapped': 0, 'newly_mapped': 0, 'missing': 0}
    
    # Fetch peak channel from NWB if missing
    # (Extract factors also computes it)
    # But let's just rely on the peak channel already in the units layered file if it exists.
    # From v3 script: peak_channel_id / 128
    
    for sid in df_units['session_id'].unique():
        sid_str = str(sid)
        mask_sid = df_units['session_id'] == sid_str
        
        # We need peak_channel for these units
        # If not present, we'll need to load NWB
        if 'peak_channel' not in df_units.columns:
            df_units['peak_channel'] = np.nan
            
        nwb_files = [f for f in os.listdir(NWB_DIR) if sid_str in f and f.endswith('.nwb')]
        if not nwb_files: continue
        
        try:
            nwb_file_path = os.path.join(NWB_DIR, nwb_files[0])
            with NWBHDF5IO(nwb_file_path, 'r', load_namespaces=True) as io:
                nwb = io.read()
                units_table = nwb.units.to_dataframe()
                
                for idx in df_units[mask_sid].index:
                    u_idx = int(df_units.at[idx, 'unit_idx'])
                    pid_str = str(df_units.at[idx, 'probe_id'])
                    
                    if u_idx >= len(units_table): continue
                    
                    # Peak channel id within probe
                    peak_ch_raw = int(float(units_table.iloc[u_idx]['peak_channel_id']))
                    local_ch = peak_ch_raw % 128
                    df_units.at[idx, 'peak_channel'] = local_ch
                    
                    crossover = vflip_map.get((sid_str, pid_str))
                    if crossover is not None and not np.isnan(crossover):
                        counts['mapped'] += 1
                        if df_units.at[idx, 'layer'] == 'none' or df_units.at[idx, 'layer'] == 'unknown':
                            counts['newly_mapped'] += 1
                            
                        if local_ch < (crossover - BUFFER):
                            df_units.at[idx, 'layer'] = 'Superficial'
                        elif local_ch > (crossover + BUFFER):
                            df_units.at[idx, 'layer'] = 'Deep'
                        else:
                            df_units.at[idx, 'layer'] = 'L4'
                    else:
                        counts['missing'] += 1
        except Exception as e:
            print(f"Error processing session {sid_str}: {e}")

    # Save output
    df_units.to_csv(OUTPUT_PATH, index=False)
    print(f"Updated layer mapping saved to {OUTPUT_PATH}")
    print(f"Total units processed: {len(df_units)}")
    print(f"Successfully mapped: {counts['mapped']} units.")
    print(f"Newly mapped from improvement: {counts['newly_mapped']} units.")
    print(df_units['layer'].value_counts())

if __name__ == "__main__":
    map_layers()
