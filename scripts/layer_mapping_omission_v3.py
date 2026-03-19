"""
layer_mapping_omission_v3.py: Maps identified omission neurons to cortical layers (Superficial, L4, Deep)
using the previously calculated vFLIP2 crossover points.
Uses the latest real_omission_units_v3.csv and vflip2_summary.txt.
"""
import os
import pandas as pd
import numpy as np
from pynwb import NWBHDF5IO

# Paths
UNITS_LAYERED_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/real_omission_units_layered_v3.csv' # Using forward slashes for safety
LATENCY_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/omission_latencies_v2.csv' # Assuming latest latency file
VFLIP_SUMMARY_PATH = 'D:/Analysis/Omission/local-workspace/LFP_Extractions/vflip2_summary.txt'
NWB_DIR = 'D:/Analysis/Omission/local-workspace/data' # NWB files are now in data/
OUTPUT_PATH = 'D:/Analysis/Omission/local-workspace/checkpoints/real_omission_units_layered_v3_final.csv' # Save to a new file

def parse_vflip_summary(path):
    """Parses the vflip summary text file into a dict mapping (session, probe) -> crossover."""
    mappings = {}
    if not os.path.exists(path): 
        print(f"vFLIP summary not found at {path}. Layer mapping will be incomplete.")
        return mappings
    with open(path, 'r') as f:
        for line in f:
            if 'Session' in line and 'Probe' in line:
                # Format: Session 230629: Probe 0: Crossover at channel 30.50
                parts = line.split()
                sid = parts[1].replace(':', '')
                pid = parts[3].replace(':', '')
                try:
                    crossover = float(parts[-1])
                    mappings[(sid, pid)] = crossover
                except: 
                    # Ignore lines that don't parse correctly
                    pass
    return mappings

def map_layers():
    if not os3.path.exists(UNITS_LAYERED_PATH):
        print(f"Error: Units layered file not found at {UNITS_LAYERED_PATH}")
        return
        
    df_omit = pd.read_csv(UNITS_LAYERED_PATH)
    vflip_map = parse_vflip_summary(VFLIP_SUMMARY_PATH)
    print(f"Loaded {len(vflip_map)} crossover mappings.")
    
    # Standardize column names for merging if needed (based on previous versions)
    if 'sid' in df_omit.columns:
        df_omit = df_omit.rename(columns={'sid': 'session_id', 'pid': 'probe_id', 'u': 'unit_idx'})
    
    BUFFER = 5 
    df_omit['peak_channel'] = np.nan
    df_omit['crossover_ch'] = np.nan
    df_omit['layer'] = 'unknown'
    
    for sid in df_omit['session_id'].unique():
        sid_str = str(int(sid)) # Ensure it's a string like '230831'
        print(f"  Processing Session {sid_str}...")
        
        nwb_files = [f for f in os.listdir(NWB_DIR) if sid_str in f and f.endswith('.nwb')]
        if not nwb_files: 
            print(f"    No NWB file found for session {sid_str}. Skipping.")
            continue
        
        try:
            nwb_file_path = os.path.join(NWB_DIR, nwb_files[0])
            with NWBHDF5IO(nwb_file_path, 'r', load_namespaces=True) as io:
                nwb = io.read()
                units_table = nwb.units.to_dataframe()
                
                mask = df_omit['session_id'] == sid
                for idx in df_omit[mask].index:
                    u_idx = int(df_omit.at[idx, 'unit_idx'])
                    probe_id = str(int(df_omit.at[idx, 'probe_id'])) # Ensure probe_id is string for dict lookup
                    
                    if u_idx >= len(units_table): continue
                    
                    # Get peak channel and map to local probe index
                    peak_ch_raw = int(float(units_table.iloc[u_idx]['peak_channel_id']))
                    local_ch = peak_ch_raw % 128 # Assuming 128 channels per probe
                    df_omit.at[idx, 'peak_channel'] = local_ch
                    
                    crossover = vflip_map.get((sid_str, probe_id))
                    if crossover is not None and not np.isnan(crossover):
                        df_omit.at[idx, 'crossover_ch'] = crossover
                        if local_ch < (crossover - BUFFER):
                            df_omit.at[idx, 'layer'] = 'Superficial'
                        elif local_ch > (crossover + BUFFER):
                            df_omit.at[idx, 'layer'] = 'Deep'
                        else:
                            df_omit.at[idx, 'layer'] = 'L4'
        except Exception as e:
            print(f"    Error processing {sid_str}: {e}")

    df_omit.to_csv(OUTPUT_PATH, index=False)
    print(f"
Layer mapping complete. Saved to {OUTPUT_PATH}")
    print(df_omit['layer'].value_counts())

if __name__ == "__main__":
    main()
