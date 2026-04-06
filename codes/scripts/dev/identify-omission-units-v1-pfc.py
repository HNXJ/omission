
import numpy as np
import pandas as pd
import glob
import os
import json
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
CHANNELS_PER_PROBE = 128
TARGET_SESSIONS = ['230630', '230816', '230830']
OMISSION_WINDOW = (4093, 4624) # ms

def get_unit_to_area_map(nwb_path):
    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            electrodes_df = nwbfile.electrodes.to_dataframe()
            probe_units = defaultdict(list)
            for idx, unit in units_df.iterrows():
                peak_chan_id = int(float(unit['peak_channel_id']))
                if peak_chan_id not in electrodes_df.index: continue
                probe_id = int(peak_chan_id // CHANNELS_PER_PROBE)
                probe_units[probe_id].append((idx, peak_chan_id))
            for probe_id, units in probe_units.items():
                units.sort(key=lambda x: x[0])
                for local_idx, (global_idx, peak_chan_id) in enumerate(units):
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
                    unit_map[(probe_id, local_idx)] = assigned_area
    except: pass
    return unit_map

def identify_omission_units():
    results = {}
    
    for session_id in TARGET_SESSIONS:
        print(f"Identifying omission units in session {session_id}...")
        results[session_id] = {'V1': [], 'PFC': []}
        
        nwb_path = glob.glob(f'data/sub-*_ses-{session_id}_rec.nwb')[0]
        unit_to_area = get_unit_to_area_map(nwb_path)
        
        # We need RRRR (Standard) for comparison and AAAX (Omission)
        # Wait, AAAX has omission at p4. RRRR has stimulus at p4.
        
        spk_files_aaaa = glob.glob(f'data/ses{session_id}-units-probe*-spk-RRRR.npy')
        spk_files_aaax = glob.glob(f'data/ses{session_id}-units-probe*-spk-AAAX.npy')
        
        for f_aaax in spk_files_aaax:
            probe_id = int(re.search(r'probe(\d+)', f_aaax).group(1))
            f_aaaa = next((f for f in spk_files_aaaa if f"probe{probe_id}" in f), None)
            if not f_aaaa: continue
            
            data_aaax = np.load(f_aaax, mmap_mode='r')
            data_aaaa = np.load(f_aaaa, mmap_mode='r')
            
            for unit_idx in range(data_aaax.shape[1]):
                area = unit_to_area.get((probe_id, unit_idx))
                if area not in ['V1', 'PFC']: continue
                
                # Omission window: 4093-4624ms (Sample indices: 4093:4624)
                # Stimulus windows in RRRR:
                # p1: 1000:1531, p2: 2031:2562, p3: 3062:3593, p4: 4093:4624
                # Fixation: 0:1000
                
                spk_aaax = data_aaax[:, unit_idx, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]]
                om_rate = np.mean(spk_aaax) * 1000
                
                # Check baseline/stimulus rates in RRRR
                fix_rate = np.mean(data_aaaa[:, unit_idx, 0:1000]) * 1000
                p1_rate = np.mean(data_aaaa[:, unit_idx, 1000:1531]) * 1000
                p2_rate = np.mean(data_aaaa[:, unit_idx, 2031:2562]) * 1000
                p3_rate = np.mean(data_aaaa[:, unit_idx, 3062:3593]) * 1000
                p4_rate = np.mean(data_aaaa[:, unit_idx, 4093:4624]) * 1000 # This is the stim response at same time
                
                # "Real" omission unit criteria:
                # 1. OM rate > FIX rate
                # 2. OM rate > STIM rates (p1, p2, p3)
                # 3. OM rate > P4 STIM rate (optional but strong)
                
                if om_rate > fix_rate and om_rate > p1_rate and om_rate > p2_rate and om_rate > p3_rate:
                    results[session_id][area].append({
                        'probe_id': probe_id,
                        'unit_idx': unit_idx,
                        'om_rate': float(om_rate),
                        'fix_rate': float(fix_rate),
                        'max_stim_rate': float(max(p1_rate, p2_rate, p3_rate))
                    })

    os.makedirs('checkpoints', exist_ok=True)
    with open('checkpoints/omission_units_v1_pfc.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\nSaved {sum(len(v['V1']) + len(v['PFC']) for v in results.values())} omission units.")

if __name__ == '__main__':
    identify_omission_units()
