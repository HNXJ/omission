import numpy as np
import pandas as pd
import glob
import os
import re
from scipy.stats import ttest_ind, pearsonr
from pynwb import NWBHDF5IO
from collections import defaultdict
from pathlib import Path
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

# Constants
CHANNELS_PER_PROBE = 128
FS = 1000
BIN_MS = 50

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

# Timing Windows (Samples relative to Code 101.0 at 1000)
WINDOWS = {
    'fx': (500, 1000),
    'p1': (1000, 1531), 'd1': (1531, 2031),
    'p2': (2031, 2562), 'd2': (2562, 3062),
    'p3': (3062, 3593), 'd3': (3593, 4093),
    'p4': (4093, 4624), 'd4': (4624, 5124)
}

def get_unit_metadata(nwb_path):
    """Extracts area and depth for all units."""
    unit_meta = []
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            elec_df = nwbfile.electrodes.to_dataframe()
            
            # Map probe/local_idx to area
            for idx, unit in units_df.iterrows():
                p_id = int(float(unit['peak_channel_id']))
                probe_id = p_id // CHANNELS_PER_PROBE
                local_idx = idx # Assumes global index corresponds to local order within probe (need to verify)
                
                # More robust local_idx calculation
                # (This part is tricky if multiple probes are in one NWB)
                
                elec = elec_df.loc[p_id]
                raw = elec.get('location', elec.get('label', 'unknown'))
                if isinstance(raw, bytes): raw = raw.decode('utf-8')
                area = raw # Placeholder for refined area mapping
                
                unit_meta.append({
                    'global_idx': idx,
                    'probe_id': probe_id,
                    'channel': p_id,
                    'area': area
                })
    except Exception as e:
        print(f"Error processing {nwb_path}: {e}")
    return unit_meta

def classify_neurons_refined():
    """Enhanced classification: selective, agnostic, preference, omit, eye."""
    checkpoint_dir = PROCESSED_DATA_DIR
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Load session mappings
    sessions = sorted(list(set([re.search(r'ses-(\d+)', f).group(1) for f in glob.glob(str(DATA_DIR / 'sub-*_ses-*_rec.nwb'))])))
    
    # Load area mapping from existing categories
    area_df = pd.read_csv(os.path.join(checkpoint_dir, 'neuron_categories.csv'))
    area_df['session'] = area_df['session'].astype(str)
    
    all_units = []
    
    for ses in sessions:
        print(f"Processing Session {ses}...")
        ses_areas = area_df[area_df['session'] == ses]
        area_map = {(row['probe'], row['unit_idx']): row['area'] for _, row in ses_areas.iterrows()}
        
        # Load SPK data for key conditions
        conds = ['AAAB', 'BBBA', 'AXAB', 'BXBA']
        spk_data = {}
        for c in conds:
            files = glob.glob(str(DATA_DIR / f'ses{ses}-units-probe*-spk-{c}.npy'))
            for f in files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                if c not in spk_data: spk_data[c] = {}
                spk_data[c][p_id] = np.load(f, mmap_mode='r')
        
        # Load Behavioral data (Eye)
        eye_data = {}
        for c in conds:
            f = glob.glob(str(DATA_DIR / f'ses{ses}-behavioral-{c}.npy'))
            if f: eye_data[c] = np.load(f[0], mmap_mode='r')
            
        # Iterate through probes and units
        if 'AAAB' not in spk_data: continue
        probes = sorted(list(spk_data['AAAB'].keys()))
        
        for p in probes:
            n_units = spk_data['AAAB'][p].shape[1]
            for u in range(n_units):
                # 1. Stimulus Response (AAAB vs BBBA in P1)
                fr_a = np.mean(spk_data['AAAB'][p][:, u, 1000:1531], axis=1) * 1000
                fr_b = np.mean(spk_data['BBBA'][p][:, u, 1000:1531], axis=1) * 1000 if p in spk_data.get('BBBA', {}) else None
                base = np.mean(spk_data['AAAB'][p][:, u, 500:1000], axis=1) * 1000
                
                resp_a = np.mean(fr_a) - np.mean(base)
                resp_b = np.mean(fr_b) - np.mean(base) if fr_b is not None else 0
                
                # Selectivity (t-test A vs B)
                p_val_select = 1.0
                if fr_b is not None:
                    _, p_val_select = ttest_ind(fr_a, fr_b)
                
                is_stim = abs(resp_a) > 2 or abs(resp_b) > 2
                is_selective = p_val_select < 0.05 and is_stim
                is_agnostic = p_val_select >= 0.05 and is_stim
                
                # 2. Omission Preference (AXAB vs AAAB in P2 window)
                # AXAB has Omission at P2 (2031-2562)
                fr_omit = np.mean(spk_data['AXAB'][p][:, u, 2031:2562], axis=1) * 1000 if p in spk_data.get('AXAB', {}) else None
                fr_normal = np.mean(spk_data['AAAB'][p][:, u, 2031:2562], axis=1) * 1000
                
                p_val_omit = 1.0
                if fr_omit is not None:
                    _, p_val_omit = ttest_ind(fr_omit, fr_normal)
                
                is_omit = p_val_omit < 0.05 and np.mean(fr_omit) > np.mean(fr_normal)
                
                # 3. Eye Correlation
                # Correlate Trial FR with Mean Eye Velocity in P1
                # Velocity = sqrt(dx^2 + dy^2)
                p_val_eye = 1.0
                if 'AAAB' in eye_data:
                    ex = eye_data['AAAB'][:, 0, 1000:1531]
                    ey = eye_data['AAAB'][:, 1, 1000:1531]
                    vx = np.gradient(ex, axis=1)
                    vy = np.gradient(ey, axis=1)
                    v_mag = np.mean(np.sqrt(vx**2 + vy**2), axis=1)
                    if len(fr_a) == len(v_mag):
                        _, p_val_eye = pearsonr(fr_a, v_mag)
                
                is_eye = p_val_eye < 0.05
                
                # Consolidate Category
                categories = []
                if is_selective: categories.append('Stim-Selective')
                if is_agnostic: categories.append('Stim-Agnostic')
                if is_omit: categories.append('Omit-Pref')
                if is_eye: categories.append('Eye-Corr')
                if not categories: categories.append('Other')
                
                all_units.append({
                    'session': ses,
                    'probe': p,
                    'unit_idx': u,
                    'area': area_map.get((p, u), 'unknown'),
                    'resp_a': resp_a,
                    'resp_b': resp_b,
                    'is_selective': is_selective,
                    'is_agnostic': is_agnostic,
                    'is_omit': is_omit,
                    'is_eye': is_eye,
                    'category': '|'.join(categories)
                })
                
    df = pd.DataFrame(all_units)
    df.to_csv(f'{checkpoint_dir}/enhanced_neuron_categories.csv', index=False)
    print(f"Enhanced classification saved. Count: {len(df)}")


def main(args=None):
    classify_neurons_refined()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
