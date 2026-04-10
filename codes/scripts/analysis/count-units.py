import os
import glob
from pynwb import NWBHDF5IO
import pandas as pd
from codes.functions.lfp.lfp_mapping import resolve_area_membership

# Path setup
NWB_DIR = r"D:\analysis\nwb"
OUTPUT_FILE = Path('output/unit-counts.csv')
GAMMA_LOG = Path('.gemini/gamma/unit-counting-errors.md')

def log_error(session_id, error):
    os.makedirs(os.path.dirname(GAMMA_LOG), exist_ok=True)
    with open(GAMMA_LOG, "a") as f:
        f.write(f"Session: {session_id} | Error: {str(error)}\n")

def count_units_in_session(nwb_path):
    session_id = os.path.basename(nwb_path).split('_')[0]
    total_units = 0
    good_units = 0
    
    try:
        with NWBHDF5IO(nwb_path, 'r') as io:
            nwbfile = io.read()
            units = nwbfile.units.to_dataframe()
            total_units = len(units)
            
            # Correctly identifying 'good' units (value '1.0' in string format)
            if 'quality' in units.columns:
                good_units = len(units[units['quality'] == '1.0'])
            else:
                good_units = 0 
    except Exception as e:
        log_error(session_id, e)
        return None
    
    return {"session": session_id, "total": total_units, "good": good_units}

# Execution
nwb_files = glob.glob(os.path.join(NWB_DIR, "*.nwb"))
results = []

for nwb in nwb_files:
    data = count_units_in_session(nwb)
    if data:
        results.append(data)

df = pd.DataFrame(results)
df.to_csv(OUTPUT_FILE, index=False)
print(df)
print(f"Total Good Units: {df['good'].sum()}")
