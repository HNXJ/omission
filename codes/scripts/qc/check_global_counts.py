
import glob
import os
from pynwb import NWBHDF5IO
from collections import defaultdict

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128

def check_global_counts():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    global_counts = defaultdict(int)

    for nwb_path in nwb_files:
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                if nwbfile.units is None or nwbfile.electrodes is None: continue
                
                units_df = nwbfile.units.to_dataframe()
                electrodes_df = nwbfile.electrodes.to_dataframe()

                for idx, unit in units_df.iterrows():
                    peak_chan_id = int(float(unit['peak_channel_id']))
                    if peak_chan_id not in electrodes_df.index: continue
                    elec = electrodes_df.loc[peak_chan_id]
                    raw_label = elec.get('location', elec.get('label', 'unknown'))
                    if isinstance(raw_label, bytes): raw_label = raw_label.decode('utf-8')
                    
                    clean_label = raw_label.replace('/', ',')
                    raw_areas = [a.strip() for a in clean_label.split(',')]
                    mapped_areas = []
                    for a in raw_areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped_areas.extend(m)
                        else: mapped_areas.append(m)
                    
                    num_areas = len(mapped_areas)
                    channel_in_probe = peak_chan_id % CHANNELS_PER_PROBE
                    segment_width = CHANNELS_PER_PROBE / num_areas
                    area_index = min(int(channel_in_probe // segment_width), num_areas - 1)
                    assigned_area = mapped_areas[area_index]
                    
                    if assigned_area in TARGET_AREAS:
                        global_counts[assigned_area] += 1
        except: continue

    print("\nGlobal Unit Counts across ALL sessions:")
    for area in TARGET_AREAS:
        print(f"  - {area}: {global_counts[area]}")

if __name__ == '__main__':
    check_global_counts()
