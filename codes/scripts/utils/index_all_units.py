"""
Indexer: Map all 72,480 units across all sessions/probes to NWB source files.
"""
import numpy as np
import pandas as pd
import os
from pathlib import Path

ARRAY_DIR = Path(r'D:\drive\data\arrays')
OUTPUT_CSV = Path('outputs/all_units_master_index.csv')

def create_master_index():
    all_units = []
    npy_files = [f for f in os.listdir(ARRAY_DIR) if f.endswith('.npy') and 'spk' in f]
    
    print(f"Indexing {len(npy_files)} spike array files...")
    
    for f in npy_files:
        # Expected format: ses[ID]-units-probe[ID]-spk-[COND].npy
        parts = f.split('-')
        session = parts[0].replace('ses', '')
        probe = parts[2].replace('probe', '')
        condition = parts[4].replace('.npy', '')
        
        # Load to get unit count
        arr = np.load(ARRAY_DIR / f)
        n_units = arr.shape[1]
        
        # We only need to add units once per session/probe (using the first condition found)
        # Assuming all conditions for a session/probe have the same number of units
        for u_idx in range(n_units):
            all_units.append({
                'session': session,
                'probe': int(probe),
                'unit_idx': u_idx,
                'source_nwb': f'ses{session}.nwb' # Standardized naming convention
            })
            
    # Deduplicate (since we checked multiple conditions)
    df = pd.DataFrame(all_units).drop_duplicates()
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Master index saved to {OUTPUT_CSV} with {len(df)} unique units.")

if __name__ == "__main__":
    create_master_index()
