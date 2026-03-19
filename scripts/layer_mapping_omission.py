"""
layer_mapping_omission.py: Maps identified omission neurons to cortical layers (Superficial, L4, Deep)
using the previously calculated vFLIP2 crossover points.
"""
import os
import pandas as pd
import numpy as np
from pynwb import NWBHDF5IO

OMIT_UNITS_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_v3.csv'
VFLIP_SUMMARY_PATH = r'D:\Analysis\Omission\local-workspace\LFP_Extractions\vflip2_summary.txt'
NWB_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_PATH = r'D:\Analysis\Omission\local-workspace\checkpoints\real_omission_units_layered_v3.csv'

def parse_vflip_summary(path):
    mappings = {}
    if not os.path.exists(path): return {}
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
                except: pass
    return mappings

def map_layers():
    if not os.path.exists(OMIT_UNITS_PATH):
        print(f"Omission units file not found at {OMIT_UNITS_PATH}")
        return
        
    df_omit = pd.read_csv(OMIT_UNITS_PATH)
    vflip_map = parse_vflip_summary(VFLIP_SUMMARY_PATH)
    print(f"Loaded {len(vflip_map)} crossover mappings.")
    
    if 'sid' in df_omit.columns:
        df_omit = df_omit.rename(columns={'sid': 'session_id', 'pid': 'probe_id', 'u': 'unit_idx'})
    
    BUFFER = 5 
    df_omit['peak_channel'] = np.nan
    df_omit['crossover_ch'] = np.nan
    df_omit['layer'] = 'unknown'
    
    for sid in df_omit['session_id'].unique():
        sid_str = str(int(sid))
        print(f"  Processing Session {sid_str}...")
        
        nwb_files = [f for f in os.listdir(NWB_DIR) if sid_str in f and f.endswith('.nwb')]
        if not nwb_files: continue
        
        try:
            with NWBHDF5IO(os.path.join(NWB_DIR, nwb_files[0]), 'r', load_namespaces=True) as io:
                nwb = io.read()
                units_table = nwb.units.to_dataframe()
                
                mask = df_omit['session_id'] == sid
                for idx in df_omit[mask].index:
                    u_idx = int(df_omit.at[idx, 'unit_idx'])
                    pid_str = str(int(df_omit.at[idx, 'probe_id']))
                    
                    if u_idx >= len(units_table): continue
                    
                    peak_ch_raw = int(float(units_table.iloc[u_idx]['peak_channel_id']))
                    local_ch = peak_ch_raw % 128
                    df_omit.at[idx, 'peak_channel'] = local_ch
                    
                    crossover = vflip_map.get((sid_str, pid_str))
                    if crossover is not None and not np.isnan(crossover):
                        df_omit.at[idx, 'crossover_ch'] = crossover
                        if local_ch < (crossover - BUFFER):
                            df_omit.at[idx, 'layer'] = 'Superficial'
                        elif local_ch > (crossover + BUFFER):
                            df_omit.at[idx, 'layer'] = 'Deep'
                        else:
                            df_omit.at[idx, 'layer'] = 'L4'
        except Exception as e:
            print(f"    Error {sid_str}: {e}")

    df_omit.to_csv(OUTPUT_PATH, index=False)
    print(f"\nLayer mapping complete. Saved to {OUTPUT_PATH}")
    print(df_omit['layer'].value_counts())

if __name__ == "__main__":
    map_layers()
