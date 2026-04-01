
import numpy as np
import pandas as pd
import glob
import os
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
CHANNELS_PER_PROBE = 128
# Time Windows (indices based on 1000Hz sampling)
WINDOWS = {
    'fx': (0, 1000),
    'pre': { # Delay before omission
        'RXRR': (1531, 2031), # d1
        'RRXR': (2562, 3062), # d2
        'RRRX': (3593, 4093)  # d3
    },
    'omit': { # Omission window
        'RXRR': (2031, 2562), # p2
        'RRXR': (3062, 3593), # p3
        'RRRX': (4093, 4624)  # p4
    },
    'post': { # Delay after omission
        'RXRR': (2562, 3062), # d2
        'RRXR': (3593, 4093), # d3
        'RRRX': (4624, 5124)  # d4
    }
}

def get_unit_to_area_map(nwb_path):
    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            elec_df = nwbfile.electrodes.to_dataframe()
            probe_units = defaultdict(list)
            for idx, unit in units_df.iterrows():
                p_id = int(float(unit['peak_channel_id']))
                probe_id = p_id // CHANNELS_PER_PROBE
                probe_units[probe_id].append((idx, p_id))
            for probe_id, units in probe_units.items():
                units.sort(key=lambda x: x[0])
                for local_idx, (global_idx, p_id) in enumerate(units):
                    elec = elec_df.loc[p_id]
                    raw = elec.get('location', elec.get('label', 'unknown'))
                    if isinstance(raw, bytes): raw = raw.decode('utf-8')
                    clean = raw.replace('/', ',')
                    raw_areas = [a.strip() for a in clean.split(',')]
                    mapped = []
                    for a in raw_areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped.extend(m)
                        else: mapped.append(m)
                    sw = CHANNELS_PER_PROBE / len(mapped)
                    area = mapped[min(int((p_id % CHANNELS_PER_PROBE) // sw), len(mapped)-1)]
                    unit_map[(probe_id, local_idx)] = {
                        'area': area,
                        'chan': p_id % CHANNELS_PER_PROBE,
                        'global_idx': global_idx
                    }
    except: pass
    return unit_map

def extract_factors():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    
    # Load Layer info
    layer_df = pd.read_csv('checkpoints/real_omission_units_layered_v3.csv')
    layer_map = {}
    for _, row in layer_df.iterrows():
        layer_map[(str(row['session_id']), int(row['probe_id']), int(row['unit_idx']))] = row['layer']

    all_rows = []

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Extracting factors for session {session_id}...")
        u_map = get_unit_to_area_map(nwb_path)
        
        # Load all condition data for this session
        cond_data = {}
        probes_in_session = set([k[0] for k in u_map.keys()])
        for cond in ['RXRR', 'RRXR', 'RRRX']:
            cond_data[cond] = {}
            for p in probes_in_session:
                f = glob.glob(f'data/ses{session_id}-units-probe{p}-spk-{cond}.npy')
                if f: cond_data[cond][p] = np.load(f[0], mmap_mode='r')

        for (probe_id, local_idx), meta in u_map.items():
            row = {
                'session': session_id,
                'area': meta['area'],
                'channel': meta['chan'],
                'layer': layer_map.get((session_id, probe_id, local_idx), 'none')
            }
            
            # Extract metrics for each condition/interval
            for cond in ['RXRR', 'RRXR', 'RRRX']:
                if probe_id not in cond_data[cond]: continue
                data = cond_data[cond][probe_id][:, local_idx, :]
                
                # Cross-trial variance trace
                # Shape: (6000,)
                var_trace = np.var(data, axis=0, ddof=1)
                
                for interval in ['fx', 'pre', 'omit', 'post']:
                    if interval == 'fx':
                        start, end = WINDOWS['fx']
                    else:
                        start, end = WINDOWS[interval][cond]
                    
                    segment = data[:, start:end]
                    var_segment = var_trace[start:end]
                    
                    # 1. Mean FR
                    row[f'{cond}_{interval}_mean_fr'] = np.mean(segment) * 1000
                    
                    # 2. STD ISI
                    trial_isis = []
                    for t in range(segment.shape[0]):
                        spk_times = np.where(segment[t, :] == 1)[0]
                        if len(spk_times) > 1:
                            trial_isis.extend(np.diff(spk_times).tolist())
                    row[f'{cond}_{interval}_std_isi'] = np.std(trial_isis) if trial_isis else 0
                    
                    # 3. Mean Variability
                    row[f'{cond}_{interval}_mean_var'] = np.mean(var_segment)
                    
                    # 4. STD Variability
                    row[f'{cond}_{interval}_std_var'] = np.std(var_segment)
            
            all_rows.append(row)

    df = pd.DataFrame(all_rows)
    os.makedirs('checkpoints', exist_ok=True)
    df.to_csv('checkpoints/omission_neurons_r_factors.csv', index=False)
    print(f"Saved 48-factor matrix with {len(df)} neurons.")

if __name__ == '__main__':
    extract_factors()
