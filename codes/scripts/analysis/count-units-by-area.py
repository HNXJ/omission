import os
import glob
from pynwb import NWBHDF5IO
import pandas as pd
from codes.functions.lfp.lfp_mapping import resolve_area_membership

# Path setup
NWB_DIR = r"D:\analysis\nwb"
OUTPUT_FILE = Path('output/unit-counts-by-area.csv')

# Mapping logic: Need to map peak_channel_id to area per session
def get_unit_area(session_id, peak_channel_id):
    # Mapping channel to area for SPK:
    # 0-127 -> probe 0, 128-255 -> probe 1, 256-383 -> probe 2
    probe_id = peak_channel_id // 128
    
    membership = resolve_area_membership(session_id, probe_id)
    local_ch = peak_channel_id % 128
    
    for area, channels in membership.items():
        if local_ch in channels:
            return area
    return "Unknown"

# Execution
nwb_files = glob.glob(os.path.join(NWB_DIR, "*.nwb"))
all_unit_data = []

for nwb in nwb_files:
    session_id = os.path.basename(nwb).split('_')[1].split('-')[1] # Extracting 6-digit ID
    try:
        with NWBHDF5IO(nwb, 'r') as io:
            nwbfile = io.read()
            units = nwbfile.units.to_dataframe()
            # Filter for good units
            good_units = units[units['quality'] == '1.0']
            
            for _, row in good_units.iterrows():
                area = get_unit_area(session_id, int(float(row['peak_channel_id'])))
                all_unit_data.append({"session": session_id, "area": area})
    except Exception as e:
        print(f"Error processing {session_id}: {e}")

# Aggregate
df = pd.DataFrame(all_unit_data)
area_counts = df.groupby('area').size()
print(area_counts)
area_counts.to_csv(OUTPUT_FILE)
