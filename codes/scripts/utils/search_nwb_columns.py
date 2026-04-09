import pynwb
from pynwb import NWBHDF5IO
from pathlib import Path
import re

# NWB directory
NWB_DIR = Path(r'D:\analysis\nwb')
f = NWB_DIR / 'sub-C31o_ses-230816_rec.nwb'

def search_columns(nwb, target_keywords):
    """Searches for columns matching target keywords in intervals tables."""
    found = {}
    for table_name in nwb.intervals:
        colnames = nwb.intervals[table_name].colnames
        for col in colnames:
            for kw in target_keywords:
                if re.search(kw, col, re.IGNORECASE):
                    if table_name not in found: found[table_name] = []
                    if col not in found[table_name]: found[table_name].append(col)
    return found

with NWBHDF5IO(str(f), 'r') as io:
    nwb = io.read()
    keywords = ['condition', 'block', 'stimulus']
    results = search_columns(nwb, keywords)
    
    print("Found matching columns in intervals tables:")
    for table, cols in results.items():
        print(f"Table: {table}")
        for col in cols:
            print(f"  - {col}")
            # Sample data
            data = nwb.intervals[table][col][:]
            print(f"    Sample: {data[:5]}")
