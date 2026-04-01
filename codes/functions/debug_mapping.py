
import pynwb
from pynwb import NWBHDF5IO
import pandas as pd
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128

def debug_session_mapping():
    nwb_path = 'data/sub-C31o_ses-230818_rec.nwb'
    unit_map = {}
    with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
        nwbfile = io.read()
        units_df = nwbfile.units.to_dataframe()
        electrodes_df = nwbfile.electrodes.to_dataframe()
        for idx, unit in units_df.iterrows():
            peak_chan_id = int(float(unit['peak_channel_id']))
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
            area_index = int(channel_in_probe // segment_width)
            area_index = min(area_index, num_areas - 1)
            assigned_area = mapped_areas[area_index]
            
            probe_id = int(peak_chan_id // CHANNELS_PER_PROBE)
            print(f"DEBUG: Unit {idx}, PeakChan {peak_chan_id} -> Probe {probe_id}, Area '{assigned_area}'")

if __name__ == '__main__':
    debug_session_mapping()
