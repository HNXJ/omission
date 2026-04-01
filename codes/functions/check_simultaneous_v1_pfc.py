
import glob
import os
from pynwb import NWBHDF5IO
from collections import defaultdict

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
CHANNELS_PER_PROBE = 128

def list_session_areas():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    session_areas = {}

    for nwb_path in nwb_files:
        session_id = nwb_path.split('ses-')[1].split('_')[0]
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                if nwbfile.electrodes is None: continue
                electrodes_df = nwbfile.electrodes.to_dataframe()
                
                # Get unique locations/labels
                raw_labels = electrodes_df.get('location', electrodes_df.get('label', 'unknown')).unique()
                
                mapped_set = set()
                for raw_label in raw_labels:
                    if isinstance(raw_label, bytes): raw_label = raw_label.decode('utf-8')
                    clean_label = raw_label.replace('/', ',')
                    areas = [a.strip() for a in clean_label.split(',')]
                    for a in areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped_set.update(m)
                        else: mapped_set.add(m)
                
                session_areas[session_id] = sorted(list(mapped_set))
        except: continue

    print("\n--- Session-Area Availability ---")
    for ses, areas in session_areas.items():
        v1_pfc = "V1" in areas and "PFC" in areas
        status = "[V1+PFC!]" if v1_pfc else ""
        print(f"Ses {ses}: {', '.join(areas)} {status}")

if __name__ == '__main__':
    list_session_areas()
