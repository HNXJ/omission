from codes.config.paths import PROJECT_ROOT

from pynwb import NWBHDF5IO
import pandas as pd
import os
import sys

def extract_trial_metadata(nwb_path, session_id):
    output_path = f"{PROJECT_ROOT}/ses-{session_id}_trials.csv"
    
    if os.path.exists(output_path):
        print(f"Metadata already exists for {session_id}. Skipping.")
        return
    
    print(f"Opening {nwb_path}...")
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwb = io.read()
            intervals = nwb.intervals
            target_table = intervals.get('omission_glo_passive') or intervals.get('trials')
            
            if target_table:
                df = target_table.to_dataframe()
                df.to_csv(output_path, index=False)
                print(f"Saved {len(df)} trials to {output_path}")
            else:
                print("No suitable interval table found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_metadata.py <nwb_path> <session_id>")
    else:
        extract_trial_metadata(sys.argv[1], sys.argv[2])
