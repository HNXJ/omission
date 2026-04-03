---
name: analysis-master-npy-export
description: Provides an optimized and granular export pipeline for converting behavioral, LFP, and neural spiking data from Neurodata Without Borders (NWB) files into aligned, windowed NumPy (.npy) arrays. This is essential for preparing data for downstream analysis, machine learning models, and visualization tools.
---
# SKILL: analysis-master-npy-export

## Description
This skill implements a robust and optimized pipeline for extracting and transforming raw neurophysiological and behavioral data from Neurodata Without Borders (NWB) files into a standardized NumPy (.npy) array format. It focuses on granular control, aligning all data streams (behavioral events, LFP, and spike times) to a common reference event (e.g., first stimulus onset) and extracting them within a specified time window. By utilizing chunked block-reads, the process is memory-efficient, making it suitable for large datasets. The resulting `.npy` files are directly amenable for further analysis, including population coding, machine learning, and advanced statistical modeling, promoting reproducibility and data interchangeability.

## Core Tasks
1.  **Trial Masking**: Utilizes external `jnwb` library functions (`jnwb.oglo_v2.get_oglo_trial_masks_v2`) to categorize trials into different experimental conditions (e.g., 'RRRR', 'RXRR', 'RRXR', 'RRRX').
2.  **Event Alignment**: Identifies a common alignment point across trials (e.g., the onset of the first stimulus, Code 101.0) and uses this to center the extracted data windows.
3.  **Chunked Data Extraction**: Reads LFP, eye, pupil, reward, and spike data from NWB acquisition and units modules in optimized memory chunks, reducing peak memory usage.
4.  **Windowed Data Export**: Extracts data within a fixed temporal window (e.g., 1000ms before alignment to 5000ms after, totaling 6000ms) for each trial.
5.  **NumPy Serialization**: Saves the processed behavioral, LFP, and spike data for each session and condition into individual NumPy (.npy) files, adhering to a consistent naming convention.

## Inputs
*   **NWB Files**: `.nwb` files located in `data/nwb/`.
*   **`jnwb` library**: A custom Python library (`D:\Analysis\jnwbepos\jnwb`) providing trial masking functionalities.
*   **Configuration**:
    *   `NWB_DIR`: Path to the directory containing NWB files.
    *   `DATA_DIR`: Path to the output directory for `.npy` files.
    *   `OMISSION_WINDOW`: Tuple defining the time window (e.g., `(1000ms_before, 5000ms_after)`).
    *   `TRIAL_CHUNK_SIZE`: Number of trials to process in each memory chunk.

## Outputs
*   **Behavioral NumPy Files**: `data/arrays/ses<session_id>-behavioral-<condition_name>.npy` (Shape: `(n_trials, 4, 6000)`, `float32`) containing eye x, eye y, pupil, and reward data.
*   **LFP NumPy Files**: `data/arrays/ses<session_id>-probe<probe_id>-lfp-<condition_name>.npy` (Shape: `(n_trials, 128, 6000)`, `float32`) for each probe.
*   **Spike NumPy Files**: `data/arrays/ses<session_id>-units-probe<probe_id>-spk-<condition_name>.npy` (Shape: `(n_trials, n_units_per_probe, 6000)`, `uint8`) for each probe.

## Example Use

```python
import os
import sys
import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO
from types import SimpleNamespace # For mocking NWB objects
import gc

# --- Mocking constants and external dependencies ---
NWB_DIR_MOCK = 'data/nwb'
DATA_DIR_MOCK = 'data/arrays'

# Mock jnwb.oglo_v2.get_oglo_trial_masks_v2
def mock_get_oglo_trial_masks_v2(trials_df):
    masks = {
        'RRRR': trials_df['trial_num'] % 2 == 0, # Even trials
        'RXRR': trials_df['trial_num'] % 2 != 0  # Odd trials
    }
    return masks

# Mock NWB components
class MockUnits:
    def __init__(self, spike_times_list, peak_channel_ids):
        self._spike_times = spike_times_list
        self._peak_channel_ids = peak_channel_ids
    
    def get_unit_spike_times(self, u_idx):
        return self._spike_times[u_idx]

    @property
    def spike_times(self): # Mock for len(nwb.units)
        return self._spike_times

    def __len__(self):
        return len(self._spike_times)

    def __getitem__(self, key): # Mock for nwb.units['peak_channel_id']
        if key == 'peak_channel_id':
            return self._peak_channel_ids
        raise KeyError(f"MockUnits has no key {key}")

class MockAcquisitionObject(SimpleNamespace):
    def __init__(self, data_shape, rate=1000.0, starting_time=0.0):
        super().__init__()
        self.data = np.random.rand(*data_shape) # Simulate actual data
        self.rate = rate
        self.starting_time = starting_time
        self.timestamps = np.arange(0, data_shape[-1]/rate, 1/rate)

class MockNWBFile(SimpleNamespace):
    def __init__(self, session_id, n_trials=10, n_units=2, n_lfp_channels=128):
        super().__init__()
        self.session_id = session_id

        # Mock trials_df
        self.intervals = {
            'omission_glo_passive': pd.DataFrame({
                'trial_num': np.arange(n_trials),
                'start_time': np.arange(n_trials) * 10.0, # 10s per trial
                'stop_time': np.arange(n_trials) * 10.0 + 9.0,
                'codes': ['101.0' for _ in range(n_trials)] # All have p1 onset
            })
        }
        self.intervals['omission_glo_passive'].to_dataframe = lambda: self.intervals['omission_glo_passive']

        # Mock units
        mock_spike_times = [np.sort(np.random.rand(np.random.randint(50, 150)) * (n_trials * 10.0)) for _ in range(n_units)]
        mock_peak_channel_ids = [str(i * 128) for i in range(n_units)] # Mock: unit 0 on probe 0, unit 1 on probe 1
        self.units = MockUnits(mock_spike_times, mock_peak_channel_ids)

        # Mock acquisition (LFP, Eye, Pupil, Reward)
        self.acquisition = {
            'lfp_probe0': MockAcquisitionObject(data_shape=(n_lfp_channels, 60000)), # 1 minute of data
            'lfp_probe1': MockAcquisitionObject(data_shape=(n_lfp_channels, 60000)),
            'eye_1_tracking': MockAcquisitionObject(data_shape=(2, 60000)), # x,y coords
            'pupil_1_tracking': MockAcquisitionObject(data_shape=(1, 60000)),
            'reward_1_tracking': MockAcquisitionObject(data_shape=(1, 60000))
        }
        self.acquisition.get = lambda k: self.acquisition.get(k) # Mock get method

class MockNWBHDF5IO:
    def __init__(self, path, mode, load_namespaces=True):
        self.path = path
        self.mode = mode
        self.session_id = path.split('ses-')[1].split('_')[0]

    def __enter__(self):
        self.nwbfile = MockNWBFile(self.session_id)
        return self.nwbfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Redefine export_session_granular function using mocks ---
def mock_export_session_granular(nwb_path, session_id):
    print(f"
>>> Optimized Granular Export (Mock): {session_id}")
    
    with MockNWBHDF5IO(nwb_path, 'r') as io:
        nwb = io.read()
        trials_df = nwb.intervals['omission_glo_passive'].to_dataframe()
        masks = mock_get_oglo_trial_masks_v2(trials_df) # Use mock mask getter
        
        # Reference Point: Code 101.0 (First Stimulus)
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

            TRIAL_CHUNK_SIZE = 2 # Small chunk size for mock
            for start_idx in range(0, n_cond_trials, TRIAL_CHUNK_SIZE):
                end_idx = min(start_idx + TRIAL_CHUNK_SIZE, n_cond_trials)
                trial_chunk = cond_trials.iloc[start_idx:end_idx]
                
                t_min = trial_chunk['p1_time'].min() - 1.1 # Adjusted for mock
                t_max = trial_chunk['p1_time'].max() + 5.1 # Adjusted for mock
                
                def get_block(obj, t_start, t_end):
                    if obj is None: return None, 0, 0
                    rate = obj.rate or 1000.0
                    t0 = obj.starting_time if obj.starting_time is not None else (obj.timestamps[0] if obj.timestamps is not None else 0.0)
                    idx_start = max(0, int((t_start - t0) * rate))
                    idx_end = int((t_end - t0) * rate)
                    block_data = obj.data[..., idx_start:idx_end] # Handle variable dimensions
                    return block_data, rate, t0 + (idx_start / rate)

                eye_block, e_rate, e_t0 = get_block(eye, t_min, t_max)
                pupil_block, p_rate, p_t0 = get_block(pupil, t_min, t_max)
                reward_block, r_rate, r_t0 = get_block(reward, t_min, t_max)
                lfp_blocks = {k: get_block(nwb.acquisition[k], t_min, t_max) for k in lfp_keys}

                for i, (_, row) in enumerate(trial_chunk.iterrows()):
                    global_i = start_idx + i
                    ts = row['p1_time'] - 1.0 # 1.0s before p1 onset
                    
                    def slice_from_block(block_info, target_arr, row_idx, axis_idx=None):
                        block, rate, t0 = block_info
                        if block is None or block.size == 0: return
                        start_sample = int((ts - t0) * rate)
                        actual_n = min(6000, block.shape[-1] - start_sample) # Check last dim for samples
                        if actual_n <= 0: return
                        
                        if axis_idx is not None: # Behavioral data
                            target_arr[row_idx, axis_idx, :actual_n] = block[axis_idx, start_sample : start_sample + actual_n]
                        else: # LFP data
                            if block.ndim == 2:
                                target_arr[row_idx, :, :actual_n] = block[:, start_sample : start_sample + actual_n]
                            else: # Handle cases where block might be 1D, should not happen for LFP
                                pass

                    slice_from_block((eye_block, e_rate, e_t0), behav_arr, global_i, 0) # Eye X
                    slice_from_block((eye_block, e_rate, e_t0), behav_arr, global_i, 1) # Eye Y
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
            np.save(os.path.join(DATA_DIR_MOCK, f'ses{session_id}-behavioral-{cond_name}.npy'), behav_arr)
            for l_key, arr in lfp_cond_arrays.items():
                np.save(os.path.join(DATA_DIR_MOCK, f'ses{session_id}-probe{l_key.split("lfp_probe")[1]}-lfp-{cond_name}.npy'), arr)
            for p_idx, arr in unit_cond_arrays.items():
                np.save(os.path.join(DATA_DIR_MOCK, f'ses{session_id}-units-probe{p_idx}-spk-{cond_name}.npy'), arr)
            
            print(f"  Saved {cond_name} data for session {session_id}.")

    gc.collect()

def mock_main():
    os.makedirs(DATA_DIR_MOCK, exist_ok=True)
    os.makedirs(NWB_DIR_MOCK, exist_ok=True)
    
    mock_session_id = '230629'
    mock_nwb_file_path = os.path.join(NWB_DIR_MOCK, f'sub-mock_ses-{mock_session_id}_rec.nwb')
    with open(mock_nwb_file_path, 'w') as f: f.write("mock NWB content") # Create dummy file
    
    mock_export_session_granular(mock_nwb_file_path, mock_session_id)
    
    # Verify outputs (simplified)
    print("
  Mock output files created:")
    print(f"  - {DATA_DIR_MOCK}/ses{mock_session_id}-behavioral-RRRR.npy (Shape: {np.load(f'{DATA_DIR_MOCK}/ses{mock_session_id}-behavioral-RRRR.npy').shape})")
    print(f"  - {DATA_DIR_MOCK}/ses{mock_session_id}-probe0-lfp-RRRR.npy (Shape: {np.load(f'{DATA_DIR_MOCK}/ses{mock_session_id}-probe0-lfp-RRRR.npy').shape})")
    print(f"  - {DATA_DIR_MOCK}/ses{mock_session_id}-units-probe0-spk-RRRR.npy (Shape: {np.load(f'{DATA_DIR_MOCK}/ses{mock_session_id}-units-probe0-spk-RRRR.npy').shape})")

    # Clean up mock environment
    import shutil
    shutil.rmtree(NWB_DIR_MOCK)
    shutil.rmtree(DATA_DIR_MOCK)
    print("
  Cleaned up mock environment.")

# --- Run the demonstration ---
if __name__ == "__main__":
    mock_main()
```