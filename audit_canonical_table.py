import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import glob
from codes.functions.io.condition_mapping import get_canonical_condition_map, resolve_condition_name

def audit_to_table(nwb_path):
    with NWBHDF5IO(str(nwb_path), 'r') as io:
        nwb = io.read()
        intervals = nwb.intervals['omission_glo_passive'].to_dataframe()
        correct_trials = intervals[intervals['correct'] == '1.0'].copy()
        
        cond_map = get_canonical_condition_map()
        correct_trials['condition_name'] = correct_trials['task_condition_number'].apply(
            lambda x: resolve_condition_name(x, cond_map)
        )
        counts = correct_trials['condition_name'].value_counts()
        
        # Ensure we have all 12 canonical conditions
        full_counts = {c: counts.get(c, 0) for c in cond_map.keys()}
        full_counts['session'] = nwb_path.name
        return full_counts

files = glob.glob(r'D:/analysis/nwb/*.nwb')
data = [audit_to_table(Path(f)) for f in files]
df = pd.DataFrame(data)
# Reorder: session first
cols = ['session'] + sorted([c for c in df.columns if c != 'session'])
df = df[cols]
df.to_markdown(r'D:/drive/omission/context/nwb-data-oglo-session-by-session-table.md', index=False)
print("Canonical condition table generated.")
