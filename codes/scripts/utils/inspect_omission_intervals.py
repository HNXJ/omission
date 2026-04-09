import pynwb
from pynwb import NWBHDF5IO
from pathlib import Path

# Inspecting event names in nwb.intervals
NWB_DIR = Path(r'D:\analysis\nwb')
f = NWB_DIR / 'sub-C31o_ses-230816_rec.nwb'

with NWBHDF5IO(str(f), 'r') as io:
    nwb = io.read()
    
    # Inspect 'omission_glo_passive' table
    table_name = 'omission_glo_passive'
    if table_name in nwb.intervals:
        table = nwb.intervals[table_name]
        print(f"\n--- Inspecting {table_name} ---")
        print("Columns:", table.colnames)
        
        # Accessing data safely
        data = table.to_dataframe()
        print("\nHead of data:")
        print(data.head())
        
        # Inspect for 'event_type' or 'event_code' specifically
        if 'event_type' in table.colnames:
             print("\nUnique event types:", table['event_type'][:].unique())
        elif 'description' in table.colnames:
             print("\nDescription sample:", table['description'][:5])
