
import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import re

def get_condition_map():
    return {
        'AAAB': [1, 2], 'AXAB': [3], 'AAXB': [4], 'AAAX': [5],
        'BBBA': [6, 7], 'BXBA': [8], 'BBXA': [9], 'BBBX': [10],
        'RRRR': list(range(11, 27)), 'RXRR': list(range(27, 35)),
        'RRXR': [35, 37, 39, 41], 'RRRX': [36, 38, 40, 42] + list(range(43, 51)),
    }

def get_condition_name(condition_number, condition_map):
    if pd.isna(condition_number): return 'Unknown'
    try:
        condition_number = int(float(condition_number))
        for name, numbers in condition_map.items():
            if condition_number in numbers: return name
    except (ValueError, TypeError): return 'Unknown'
    return 'Unknown'

def get_session_name(nwb_path):
    match = re.search(r'ses-(\d+)_rec', nwb_path.name)
    return match.group(1) if match else nwb_path.stem

nwb_files = sorted(list(set([
    'D:/analysis/nwb/sub-C31o_ses-230630_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230816_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230818_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230823_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230825_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230830_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230831_rec.nwb',
    'D:/analysis/nwb/sub-C31o_ses-230901_rec.nwb',
    'D:/analysis/nwb/sub-V198o_ses-230629_rec.nwb',
    'D:/analysis/nwb/sub-V198o_ses-230714_rec.nwb',
    'D:/analysis/nwb/sub-V198o_ses-230719_rec.nwb',
    'D:/analysis/nwb/sub-V198o_ses-230720_rec.nwb',
    'D:/analysis/nwb/sub-V198o_ses-230721_rec.nwb',
])))

condition_map = get_condition_map()
all_results = []

for file_path in nwb_files:
    nwb_path = Path(file_path)
    session_name = get_session_name(nwb_path)
    
    with NWBHDF5IO(str(nwb_path), 'r') as io:
        nwb = io.read()
        intervals = nwb.intervals['omission_glo_passive'].to_dataframe()
        correct_trials = intervals[intervals['correct'] == '1.0'].copy()
        
        correct_trials['condition_name'] = correct_trials['task_condition_number'].apply(
            lambda x: get_condition_name(x, condition_map)
        )
        
        trial_conditions = correct_trials.groupby('trial_num')['condition_name'].first()
        condition_counts = trial_conditions.value_counts().rename(session_name)
        all_results.append(condition_counts)

results_df = pd.concat(all_results, axis=1).fillna(0).astype(int)
results_df.columns.name = 'Session'
results_df.index.name = 'Condition'

# Add a total column
results_df['Total'] = results_df.sum(axis=1)


print(results_df.to_markdown())
