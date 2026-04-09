import pynwb
from pynwb import NWBHDF5IO
from pathlib import Path
import pandas as pd

# Target NWB
NWB_DIR = Path(r'D:\analysis\nwb')
f = NWB_DIR / 'sub-C31o_ses-230816_rec.nwb'

def inspect_correct_trials():
    with NWBHDF5IO(str(f), 'r') as io:
        nwb = io.read()
        table = nwb.intervals['omission_glo_passive']
        df = table.to_dataframe()
        
        print("Checking 'correct' column and trial event structure...")
        if 'correct' in df.columns:
            correct_trials = df[df['correct'].isin([1, 1.0])]
            print(f"Total entries: {len(df)}")
            print(f"Entries where 'correct' == 1: {len(correct_trials)}")
            
            # Print unique values in 'correct' column
            print(f"Unique values in 'correct': {df['correct'].unique()}")
            
            # Inspect the first 'correct' trial sequence
            first_correct_idx = correct_trials.index[0]
            print(f"\nExample sequence for a 'correct' trial (ID {first_correct_idx}):")
            print(df.loc[first_correct_idx:first_correct_idx+10, ['task_condition_number', 'task_sequence', 'trial_num']])
        else:
            print("Column 'correct' not found in omission_glo_passive.")

if __name__ == "__main__":
    inspect_correct_trials()
