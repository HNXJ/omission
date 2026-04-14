import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import glob
from codes.functions.io.condition_mapping import get_canonical_condition_map, resolve_condition_name

def audit_to_table(nwb_path):
    try:
        with NWBHDF5IO(str(nwb_path), 'r') as io:
            nwb = io.read()
            intervals = nwb.intervals['omission_glo_passive'].to_dataframe()
            correct_trials = intervals[intervals['correct'] == '1.0'].copy()
            
            cond_map = get_canonical_condition_map()
            correct_trials['condition_name'] = correct_trials['task_condition_number'].apply(
                lambda x: resolve_condition_name(x, cond_map)
            )
            
            unique_trials = correct_trials.groupby('trial_num').first()
            counts = unique_trials['condition_name'].value_counts()
            
            res = {c: counts.get(c, 0) for c in cond_map.keys()}
            res['Total'] = sum(res.values())
            res['session'] = nwb_path.name
            return res
    except Exception as e:
        return {'session': nwb_path.name, 'error': str(e)}

files = glob.glob(r'D:/analysis/nwb/*.nwb')
data = [audit_to_table(Path(f)) for f in files]
df = pd.DataFrame(data)
cols = ['session'] + sorted([c for c in df.columns if c not in ['session', 'Total']]) + ['Total']
df = df[cols]
df.to_markdown(r'D:/drive/omission/context/nwb-data-oglo-session-by-session-table.md', index=False)
print('Table updated with Total column.')
