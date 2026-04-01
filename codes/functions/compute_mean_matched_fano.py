
import numpy as np
import pandas as pd
import glob
import os
from pynwb import NWBHDF5IO
from collections import defaultdict
import re
import json
from scipy.ndimage import gaussian_filter1d

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128
AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
WIN_SIZE = 150 # Increased for even greater stability (Churchland 2010 + extra smoothing)
STEP = 5 

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
                    if area in AREA_ORDER: unit_map[(probe_id, local_idx)] = area
    except: pass
    return unit_map

def compute_mmff():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    time_bins = np.arange(0, 6000 - WIN_SIZE, STEP)
    stats = {area: {cond: {t: {'m': [], 'v': []} for t in time_bins} 
                    for cond in ['RRRR', 'RXRR', 'RRXR', 'RRRX']} 
             for area in AREA_ORDER}

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Collecting mean/var stats for session {session_id}...")
        u_map = get_unit_to_area_map(nwb_path)
        
        for cond in ['RRRR', 'RXRR', 'RRXR', 'RRRX']:
            spk_files = glob.glob(f'data/ses{session_id}-units-probe*-spk-{cond}.npy')
            for f in spk_files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                data = np.load(f, mmap_mode='r')
                for u_idx in range(data.shape[1]):
                    area = u_map.get((p_id, u_idx))
                    if area:
                        unit_spks = data[:, u_idx, :]
                        for t in time_bins:
                            counts = np.sum(unit_spks[:, t:t+WIN_SIZE], axis=1)
                            mu = np.mean(counts)
                            var = np.var(counts, ddof=1)
                            if mu > 0:
                                stats[area][cond][t]['m'].append(mu)
                                stats[area][cond][t]['v'].append(var)

    print("\nApplying Mean-Matching across all areas...")
    final_results = {area: {cond: [] for cond in stats[area]} for area in AREA_ORDER}

    for area in AREA_ORDER:
        for cond in stats[area]:
            all_means = []
            for t in time_bins:
                all_means.extend(stats[area][cond][t]['m'])
            
            if not all_means: continue
            
            hist_bins = np.linspace(0, max(all_means), 30)
            global_counts, _ = np.histogram(all_means, bins=hist_bins)
            target_dist = global_counts / np.sum(global_counts)

            trace = []
            for t in time_bins:
                ms = np.array(stats[area][cond][t]['m'])
                vs = np.array(stats[area][cond][t]['v'])
                
                if len(ms) < 5:
                    trace.append(np.nan)
                    continue

                current_counts, _ = np.histogram(ms, bins=hist_bins)
                valid = current_counts > 0
                scale = np.min(current_counts[valid] / target_dist[valid]) if any(valid) else 0
                
                matched_ms = []
                matched_vs = []
                
                for i in range(len(hist_bins)-1):
                    idx = np.where((ms >= hist_bins[i]) & (ms < hist_bins[i+1]))[0]
                    n_needed = int(np.floor(target_dist[i] * scale))
                    if len(idx) > 0 and n_needed > 0:
                        chosen = np.random.choice(idx, min(n_needed, len(idx)), replace=False)
                        matched_ms.extend(ms[chosen])
                        matched_vs.extend(vs[chosen])
                
                if len(matched_ms) > 2:
                    fano = np.mean(np.array(matched_vs) / np.array(matched_ms))
                    trace.append(fano)
                else:
                    trace.append(np.mean(vs/ms) if len(ms)>0 else np.nan)

            # --- Post-hoc Gaussian Smoothing (Aggressive for stability) ---
            trace = np.array(trace)
            nan_mask = np.isnan(trace)
            if not np.all(nan_mask):
                valid_idx = np.where(~nan_mask)[0]
                if len(valid_idx) > 1:
                    trace[nan_mask] = np.interp(np.where(nan_mask)[0], valid_idx, trace[valid_idx])
                else:
                    trace[nan_mask] = np.nanmean(trace)
                
                # Sigma set to 5.0 for very smooth traces
                trace = gaussian_filter1d(trace, sigma=5.0)
                trace[nan_mask] = np.nan 
            
            final_results[area][cond] = list(trace)

    os.makedirs('checkpoints', exist_ok=True)
    serializable = {area: {cond: list(final_results[area][cond]) for cond in final_results[area]} for area in final_results}
    with open('checkpoints/area_mmff_traces.json', 'w') as f:
        json.dump(serializable, f)
    
    print("Stabilized MMFF traces saved to checkpoints/area_mmff_traces.json")

if __name__ == '__main__':
    compute_mmff()
