
import numpy as np
import pandas as pd
import glob
import os
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
CHANNELS_PER_PROBE = 128

# Priority-based criteria
# Omission windows across conditions
OMIT_WIN = {
    'RXRR': (2031, 2562), # p2
    'RRXR': (3062, 3593), # p3
    'RRRX': (4093, 4624)  # p4
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
                    unit_map[(probe_id, local_idx)] = area
    except: pass
    return unit_map

def classify():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    all_classifications = []

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Classifying neurons in session {session_id}...")
        u_map = get_unit_to_area_map(nwb_path)
        
        # Load necessary conditions
        cond_data = {}
        probes = set([k[0] for k in u_map.keys()])
        for c in ['RRRR', 'RXRR', 'RRXR', 'RRRX']:
            cond_data[c] = {}
            for p in probes:
                f = glob.glob(f'data/ses{session_id}-units-probe{p}-spk-{c}.npy')
                if f: cond_data[c][p] = np.load(f[0], mmap_mode='r')

        for (probe_id, local_idx), area in u_map.items():
            if probe_id not in cond_data['RRRR']: continue
            
            # Fixation Baseline (0:1000ms)
            data_std = np.nan_to_num(cond_data['RRRR'][probe_id][:, local_idx, :])
            fx_data = data_std[:, 0:1000] # fixation window
            fx_fr = np.mean(fx_data) * 1000
            
            # Baseline SD across trials
            trial_baselines = np.mean(fx_data, axis=1) * 1000
            baseline_sd = np.std(trial_baselines)
            baseline_mean = fx_fr
            
            p1_fr = np.mean(data_std[:, 1000:1531]) * 1000

            label = 'Null'

            # 1. OMISSION (Priority 1)
            is_omit = False
            for cond, win in OMIT_WIN.items():
                if probe_id in cond_data[cond]:
                    omit_fr = np.mean(cond_data[cond][probe_id][:, local_idx, win[0]:win[1]]) * 1000
                    if omit_fr > (baseline_mean + 2 * baseline_sd):
                        is_omit = True; break
            
            if is_omit: label = 'Omit'
            
            # 2. FIXATION (Priority 2)
            elif fx_fr > 0:
                all_other_wins = [
                    np.mean(data_std[:, 1000:1531]), # p1
                    np.mean(data_std[:, 1531:2031]), # d1
                    np.mean(data_std[:, 2031:2562]), # p2
                    np.mean(data_std[:, 2562:3062]), # d2
                    np.mean(data_std[:, 3062:3593]), # p3
                    np.mean(data_std[:, 3593:4093]), # d3
                    np.mean(data_std[:, 4093:4624]), # p4
                    np.mean(data_std[:, 4624:5124])  # d4
                ]
                if all(w * 1000 < (0.5 * fx_fr) for w in all_other_wins):
                    label = 'Fix'

            # 3. STIM POSITIVE (Priority 3)
            elif any(p * 1000 > (fx_fr + 2 * baseline_sd) for p in [p1_fr]):
                label = 'Stim+'

            # 4. STIM NEGATIVE (Priority 4)
            elif any(p * 1000 < (fx_fr - 2 * baseline_sd) for p in [p1_fr]):
                label = 'Stim-'

            all_classifications.append({
                'session': session_id,
                'probe': probe_id,
                'unit_idx': local_idx,
                'area': area,
                'category': label
            })

    df = pd.DataFrame(all_classifications)
    os.makedirs('checkpoints', exist_ok=True)
    df.to_csv('checkpoints/neuron_categories.csv', index=False)
    print(f"Classification complete. {df['category'].value_counts().to_dict()}")


def main(args=None):
    classify()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
