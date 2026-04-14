import numpy as np
from pynwb import NWBHDF5IO
from pathlib import Path
import json

def audit_session(nwb_path):
    try:
        with NWBHDF5IO(str(nwb_path), 'r') as io:
            nwb = io.read()
            # Basic counts
            n_probes = 0
            for k in nwb.acquisition:
                if 'probe' in k and 'lfp' in k: n_probes += 1
            
            n_units = len(nwb.units) if nwb.units else 0
            
            # Condition counts (using the canonical condition mapper logic)
            # This is a bit complex, let's just grab the intervals
            intervals = nwb.intervals['omission_glo_passive'].to_dataframe()
            n_trials = len(intervals)
            
            # Simplified condition audit
            cond_counts = intervals['task_condition_number'].value_counts().to_dict()
            
            return {
                'session': nwb_path.name,
                'probes': n_probes,
                'units': n_units,
                'trials': n_trials,
                'condition_counts': cond_counts
            }
    except Exception as e:
        return {'session': nwb_path.name, 'error': str(e)}

if __name__ == '__main__':
    import glob
    files = glob.glob(r'D:/analysis/nwb/*.nwb')
    results = [audit_session(Path(f)) for f in files]
    with open(r'D:/drive/omission/context/nwb-data-oglo-session-by-session.md', 'w') as f:
        f.write("# NWB Data: OGLO Session-by-Session Audit\n\n")
        for res in results:
            f.write(f"## Session: {res.get('session')}\n")
            f.write(f"- **Probes**: {res.get('probes')}\n")
            f.write(f"- **Units**: {res.get('units')}\n")
            f.write(f"- **Valid Trials**: {res.get('trials')}\n")
            f.write(f"- **Conditions**: {res.get('condition_counts')}\n\n")
