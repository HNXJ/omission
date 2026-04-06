"""
master_npy_export.py: Optimized Granular Export using Chunked Block-Reads.
Alignment: Code 101.0 (First Stimulus) at Sample 1000.
Window: 1000ms before p1, 5000ms after p1 (Total 6000ms).
"""
import os
import sys
import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO
import gc
from pathlib import Path

# Add jnwb to path
sys.path.append(r'D:\Analysis\jnwb\repos\jnwb')
from jnwb.oglo_v2 import get_oglo_trial_masks_v2 as get_trial_masks

# Configuration
NWB_DIR = Path(__file__).parents[2] / "data"
DATA_DIR = Path(__file__).parents[2] / "data"

def export_session_granular(nwb_path, session_id):
    print(f"\n>>> Optimized Granular Export: {session_id}")
    
    with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
        nwb = io.read()
        trials_df = nwb.intervals['omission_glo_passive'].to_dataframe()
        masks = get_trial_masks(trials_df)
        
        # Reference Point: Code 101.0 (First Stimulus)
        # Codes are strings in this NWB
        p1_onsets = trials_df[trials_df['codes'].astype(str).str.startswith('101')][['trial_num', 'start_time']].rename(columns={'start_time': 'p1_time'})
        
        if p1_onsets.empty:
            print(f"  Error: No p1 onsets (Code 101) found for session {session_id}. Skipping.")
            return

        n_units = len(nwb.units)
        unit_probe_map = [int(float(nwb.units['peak_channel_id'][i])) // 128 for i in range(n_units)]
        print(f"  Pre-loading spike times for {n_units} units...")
        all_spike_times = [nwb.units.get_unit_spike_times(u_idx) for u_idx in range(n_units)]
        
        lfp_keys = sorted([k for k in nwb.acquisition.keys() if 'lfp' in k.lower()])
        eye = nwb.acquisition.get('eye_1_tracking')
        pupil = nwb.acquisition.get('pupil_1_tracking')
        reward = nwb.acquisition.get('reward_1_tracking')

        for cond_name, mask in masks.items():
            cond_trial_nums = trials_df[mask]['trial_num'].unique()
            cond_trials = p1_onsets[p1_onsets['trial_num'].isin(cond_trial_nums)].sort_values('p1_time')
            
            n_cond_trials = len(cond_trials)
            if n_cond_trials == 0: continue
            
            print(f"  Condition '{cond_name}': {n_cond_trials} trials.")
            
            # Initialize arrays (6000 samples total)
            behav_arr = np.zeros((n_cond_trials, 4, 6000), dtype=np.float32)
            lfp_cond_arrays = {k: np.zeros((n_cond_trials, 128, 6000), dtype=np.float32) for k in lfp_keys}
            unique_probes = sorted(list(set(unit_probe_map)))
            unit_cond_arrays = {p: np.zeros((n_cond_trials, unit_probe_map.count(p), 6000), dtype=np.uint8) for p in unique_probes}

            TRIAL_CHUNK_SIZE = 50
            for start_idx in range(0, n_cond_trials, TRIAL_CHUNK_SIZE):
                end_idx = min(start_idx + TRIAL_CHUNK_SIZE, n_cond_trials)
                trial_chunk = cond_trials.iloc[start_idx:end_idx]
                
                # Buffer for block extraction
                t_min = trial_chunk['p1_time'].min() - 1.1
                t_max = trial_chunk['p1_time'].max() + 5.1
                
                def get_block(obj, t_start, t_end):
                    if obj is None: return None, 0, 0
                    rate = obj.rate or 1000.0
                    t0 = obj.starting_time if obj.starting_time is not None else (obj.timestamps[0] if obj.timestamps is not None else 0.0)
                    idx_start = max(0, int((t_start - t0) * rate))
                    idx_end = int((t_end - t0) * rate)
                    block_data = obj.data[idx_start:idx_end]
                    return block_data, rate, t0 + (idx_start / rate)

                eye_block, e_rate, e_t0 = get_block(eye, t_min, t_max)
                pupil_block, p_rate, p_t0 = get_block(pupil, t_min, t_max)
                reward_block, r_rate, r_t0 = get_block(reward, t_min, t_max)
                lfp_blocks = {k: get_block(nwb.acquisition[k], t_min, t_max) for k in lfp_keys}

                for i, (_, row) in enumerate(trial_chunk.iterrows()):
                    global_i = start_idx + i
                    # ALIGNMENT: 1.0s before p1 onset
                    ts = row['p1_time'] - 1.0
                    
                    def slice_from_block(block_info, target_arr, row_idx, axis_idx=None):
                        block, rate, t0 = block_info
                        if block is None: return
                        start_sample = int((ts - t0) * rate)
                        actual_n = min(6000, block.shape[0] - start_sample)
                        if actual_n <= 0: return
                        
                        segment = block[start_sample : start_sample + actual_n]
                        if axis_idx is not None:
                            if segment.ndim == 2: target_arr[row_idx, axis_idx, :actual_n] = segment[:actual_n, axis_idx]
                            else: target_arr[row_idx, axis_idx, :actual_n] = segment[:actual_n].flatten()
                        else:
                            target_arr[row_idx, :, :actual_n] = segment[:actual_n, :128].T

                    slice_from_block((eye_block, e_rate, e_t0), behav_arr, global_i, 0)
                    slice_from_block((eye_block, e_rate, e_t0), behav_arr, global_i, 1)
                    slice_from_block((pupil_block, p_rate, p_t0), behav_arr, global_i, 2)
                    slice_from_block((reward_block, r_rate, r_t0), behav_arr, global_i, 3)
                    
                    for l_key in lfp_keys:
                        slice_from_block(lfp_blocks[l_key], lfp_cond_arrays[l_key], global_i)

                    for p_idx in unique_probes:
                        unit_indices = [idx for idx, p in enumerate(unit_probe_map) if p == p_idx]
                        for local_u_idx, global_u_idx in enumerate(unit_indices):
                            st = all_spike_times[global_u_idx]
                            trial_st = st[(st >= ts) & (st < ts + 6.0)]
                            indices = ((trial_st - ts) * 1000).astype(int)
                            unit_cond_arrays[p_idx][global_i, local_u_idx, indices[indices < 6000]] = 1
                
                del eye_block, pupil_block, reward_block, lfp_blocks
                gc.collect()

            # Save
            np.save(os.path.join(DATA_DIR, f'ses{session_id}-behavioral-{cond_name}.npy'), behav_arr)
            for l_key, arr in lfp_cond_arrays.items():
                np.save(os.path.join(DATA_DIR, f'ses{session_id}-probe{l_key.split("_")[1]}-lfp-{cond_name}.npy'), arr)
            for p_idx, arr in unit_cond_arrays.items():
                np.save(os.path.join(DATA_DIR, f'ses{session_id}-units-probe{p_idx}-spk-{cond_name}.npy'), arr)

    gc.collect()

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    nwb_files = [f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')]
    for f in nwb_files:
        sid = f.split('_')[1].split('-')[1]
        export_session_granular(os.path.join(NWB_DIR, f), sid)

if __name__ == "__main__":
    main()
