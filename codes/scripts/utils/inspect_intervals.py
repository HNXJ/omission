import pynwb
from pynwb import NWBHDF5IO
from pathlib import Path

# Inspecting event names in nwb.intervals
NWB_DIR = Path(r'D:\analysis\nwb')
f = NWB_DIR / 'sub-C31o_ses-230816_rec.nwb'

with NWBHDF5IO(str(f), 'r') as io:
    nwb = io.read()
    print("Available interval tables:")
    for name in nwb.intervals:
        print(f" - {name}")
    
    # Inspecting specific task intervals (often named 'trials' or similar)
    if 'trials' in nwb.intervals:
        print("\nColumns in 'trials' table:")
        print(nwb.intervals['trials'].colnames)
        
        # Checking for event codes or event names
        if 'event_names' in nwb.intervals['trials'].colnames:
            print("\nSample of event names:")
            print(nwb.intervals['trials']['event_names'][:5])
        elif 'description' in nwb.intervals['trials'].colnames:
            print("\nTable description:", nwb.intervals['trials'].description)
            
    # Also inspect 'epochs' if they exist, often used for task events
    print("\nAvailable epochs:")
    for name in nwb.epochs:
        print(f" - {name}")
