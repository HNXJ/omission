import numpy as np
import pandas as pd
from pathlib import Path
import json
from pynwb import NWBHDF5IO

# Paths
NWB_DIR = Path(r"D:\drive\data\nwb")
OUTPUT_DIR = Path(r"D:\drive\data\nwb-arrays")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SESSION_ID = "230818"

def convert_session(session_id):
    print(f"[action] Converting session {session_id}...")
    nwb_path = NWB_DIR / f"ses-{session_id}.nwb"
    if not nwb_path.exists():
        print(f"[error] NWB file not found: {nwb_path}")
        return

    with NWBHDF5IO(str(nwb_path), 'r') as io:
        nwb = io.read()
        
        # 1. Map Units
        units = nwb.units.to_dataframe()
        unit_map = {orig_id: i for i, orig_id in enumerate(units.index)}
        with open(OUTPUT_DIR / f"ses-{session_id}-unit-map.json", 'w') as f:
            json.dump(unit_map, f)
        
        # 2. Extract Data for Conditions
        # Assume conditions are in nwb.intervals['omission_glo_passive']
        trials = nwb.intervals['omission_glo_passive'].to_dataframe()
        
        # Example condition keys based on your request
        conditions = trials['condition'].unique()
        
        for cond in conditions:
            cond_trials = trials[trials['condition'] == cond]
            
            # Extract SPK: (trials, units, time)
            # This requires spike times extraction per trial
            # ...
            
            # Save: np.save(OUTPUT_DIR / f"sess-{session_id}-SPK-{cond}.npy", spk_tensor)
            # Save: np.save(OUTPUT_DIR / f"sess-{session_id}-LFP-{probe}-{cond}.npy", lfp_tensor)

    print(f"[action] Session {session_id} conversion initiated (logic structure ready).")

if __name__ == "__main__":
    convert_session(SESSION_ID)
