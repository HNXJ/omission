
import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import re

def get_condition_map():
    return {
        'AAAB': [1, 2],
        'AXAB': [3],
        'AAXB': [4],
        'AAAX': [5],
        'BBBA': [6, 7],
        'BXBA': [8],
        'BBXA': [9],
        'BBBX': [10],
        'RRRR': list(range(11, 27)),
        'RXRR': list(range(27, 35)),
        'RRXR': [35, 37, 39, 41],
        'RRRX': [36, 38, 40, 42] + list(range(43, 51)),
    }

def get_condition_name(condition_number, condition_map):
    if pd.isna(condition_number):
        return 'Unknown'
    try:
        condition_number = int(float(condition_number))
        for name, numbers in condition_map.items():
            if condition_number in numbers:
                return name
    except (ValueError, TypeError):
        return 'Unknown'
    return 'Unknown'

def main():
    # Use the same NWB file as before for consistency
    nwb_path = Path('D:/analysis/nwb/sub-C31o_ses-230630_rec.nwb')

    print(f"Processing NWB file: {nwb_path}")

    with NWBHDF5IO(str(nwb_path), 'r') as io:
        nwb = io.read()

        intervals = nwb.intervals['omission_glo_passive'].to_dataframe()

        # Filter for correct trials
        correct_trials = intervals[intervals['correct'] == '1.0'].copy()

        # Get condition map
        condition_map = get_condition_map()
        
        # Get condition names
        correct_trials['condition_name'] = correct_trials['task_condition_number'].apply(
            lambda x: get_condition_name(x, condition_map)
        )

        # We only need to count each trial once. Let's group by trial_num
        # and take the first condition name for each trial.
        trial_conditions = correct_trials.groupby('trial_num')['condition_name'].first()

        # Count the occurrences of each condition
        condition_counts = trial_conditions.value_counts()

        print("Correct trials per condition:")
        print(condition_counts)

if __name__ == "__main__":
    main()
