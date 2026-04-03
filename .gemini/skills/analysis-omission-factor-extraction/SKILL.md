---
name: analysis-omission-factor-extraction
description: Extracts a high-dimensional feature matrix (48 factors per neuron) from neural spiking data, covering mean firing rate, ISI variability, and cross-trial firing rate variability across different task conditions and temporal intervals. This is crucial for subsequent dimensionality reduction, clustering, and population dynamics analysis.
---
# SKILL: analysis-omission-factor-extraction

## Description
This skill is designed to extract a rich set of 48 neurophysiological factors for each recorded neuron, providing a high-dimensional representation of its activity patterns across various task conditions and temporal intervals relative to an omission event. These factors include measures of mean firing rate, inter-spike interval (ISI) variability, and cross-trial variability in firing rate. By quantifying these diverse aspects of neuronal activity, this skill generates a comprehensive feature matrix essential for advanced analyses such as dimensionality reduction (e.g., PCA, UMAP), neuronal clustering, and investigating population-level dynamics in response to complex stimuli or cognitive states.

## Core Tasks
1.  **`get_unit_to_area_map(nwb_path)`**:
    *   **Purpose**: Maps individual neural units from an NWB file to their assigned brain regions, original channel, and global unit index. This function integrates electrode location information with a predefined area mapping scheme.
    *   **Inputs**: Path to an NWB (.nwb) file.
    *   **Outputs**: A dictionary where keys are `(probe_id, local_unit_idx)` and values are dictionaries containing `area`, `chan`, and `global_idx` for each unit.
2.  **`extract_factors()`**:
    *   **Purpose**: Orchestrates the extraction of the 48 factors per neuron by iterating through NWB sessions, loading corresponding spike data, and computing various metrics for each unit across different conditions and predefined time windows.
    *   **Inputs**:
        *   NWB (.nwb) files from `data/nwb/`.
        *   Neural spike data as NumPy (.npy) files from `data/arrays/` (e.g., `ses<ID>-units-probe<ID>-spk-<COND>.npy`).
        *   Layer information from `checkpoints/real_omission_units_layered_v3.csv`.
        *   Predefined time `WINDOWS` (e.g., 'fx', 'pre', 'omit', 'post' for various conditions), `AREA_MAPPING`, `CHANNELS_PER_PROBE`.
    *   **Process**:
        *   Loads unit-to-area map and layer info.
        *   Loads all condition-specific spike data for a session.
        *   For each unit and for each condition (`RXRR`, `RRXR`, `RRRX`), computes:
            *   Mean Firing Rate in `fx`, `pre`, `omit`, `post` windows.
            *   STD of ISI in `fx`, `pre`, `omit`, `post` windows.
            *   Mean Cross-trial Firing Rate Variability in `fx`, `pre`, `omit`, `post` windows.
            *   STD of Cross-trial Firing Rate Variability in `fx`, `pre`, `omit`, `post` windows.
    *   **Outputs**: A Pandas DataFrame containing 48 features (factors) for each neuron, saved as a CSV file.

## Inputs
*   **NWB Files**: Located in `data/nwb/`, providing unit and electrode metadata for mapping to brain regions.
*   **Spike Data Files**: NumPy arrays (`.npy`) in `data/arrays/` named like `ses<session_id>-units-probe<probe_id>-spk-<condition>.npy`, where each array contains binned spike counts (trials x units x time).
*   **Layer Information CSV**: `checkpoints/real_omission_units_layered_v3.csv`, a CSV file containing neuron layer assignments (session_id, probe_id, unit_idx, layer).
*   **Configuration**: Internal parameters: `WINDOWS` (temporal intervals), `AREA_MAPPING` (electrode label to area mapping), `CHANNELS_PER_PROBE`.

## Outputs
*   **`checkpoints/omission_neurons_r_factors.csv`**: A CSV file containing a Pandas DataFrame where each row represents a neuron and columns are the 48 extracted factors (e.g., `RXRR_fx_mean_fr`, `RRXR_omit_std_isi`, etc.), along with session, area, channel, and layer information.

## Example Use

```python
import numpy as np
import pandas as pd
import os
import re
from collections import defaultdict
from types import SimpleNamespace # For mocking NWB objects

# --- Mocking constants and functions from extract_omission_factors.py ---
AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
CHANNELS_PER_PROBE = 128
WINDOWS = {
    'fx': (0, 1000),
    'pre': { 'RXRR': (1531, 2031) }, # Simplified for mock
    'omit': { 'RXRR': (2031, 2562) }, # Simplified for mock
    'post': { 'RXRR': (2562, 3062) }  # Simplified for mock
}

def mock_get_unit_to_area_map(nwb_path):
    unit_map = {}
    # Simulate a single unit: Probe 0, LocalIdx 0, Area V1
    unit_map[(0, 0)] = {'area': 'V1', 'chan': 10, 'global_idx': 0}
    return unit_map

# --- Mocking the extract_factors function ---
def mock_extract_factors():
    print("--- Demonstrating Omission Factor Extraction (Mock) ---")
    
    # Ensure mock directories exist
    os.makedirs('data/nwb', exist_ok=True)
    os.makedirs('data/arrays', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)

    # 1. Create a dummy NWB file
    mock_nwb_path = 'data/nwb/sub-mock_ses-230629_rec.nwb'
    with open(mock_nwb_path, 'w') as f: f.write("mock nwb content")
    
    # 2. Create a dummy real_omission_units_layered_v3.csv
    mock_layer_df = pd.DataFrame([{
        'session_id': '230629', 'probe_id': 0, 'unit_idx': 0, 'layer': 'L2/3'
    }])
    mock_layer_csv_path = 'checkpoints/real_omission_units_layered_v3.csv'
    mock_layer_df.to_csv(mock_layer_csv_path, index=False)

    # 3. Create dummy spike .npy file
    mock_cond = 'RXRR'
    # Simulate (trials, units, time_bins)
    # 10 trials, 1 unit (local_idx 0), 6000 time bins
    mock_spike_data = np.random.randint(0, 2, size=(10, 1, 6000)) # Binary spikes
    mock_spike_npy_path = f'data/arrays/ses230629-units-probe0-spk-{mock_cond}.npy'
    np.save(mock_spike_npy_path, mock_spike_data)

    # --- Replicate core logic of extract_factors ---
    nwb_files = [mock_nwb_path]
    layer_df = pd.read_csv(mock_layer_csv_path)
    layer_map = {}
    for _, row in layer_df.iterrows():
        layer_map[(str(row['session_id']), int(row['probe_id']), int(row['unit_idx']))] = row['layer']

    all_rows = []

    for nwb_path_iter in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path_iter).group(1)
        print(f"  Extracting factors for mock session {session_id}...")
        u_map = mock_get_unit_to_area_map(nwb_path_iter) # Use mock map
        
        cond_data = {}
        probes_in_session = set([k[0] for k in u_map.keys()]) # Get probe IDs from mock map
        for cond in ['RXRR']: # Simplified conditions for mock
            cond_data[cond] = {}
            for p in probes_in_session:
                cond_data[cond][p] = np.load(f'data/arrays/ses{session_id}-units-probe{p}-spk-{cond}.npy', mmap_mode='r')

        for (probe_id, local_idx), meta in u_map.items():
            row = {
                'session': session_id,
                'area': meta['area'],
                'channel': meta['chan'],
                'layer': layer_map.get((session_id, probe_id, local_idx), 'none')
            }
            
            for cond in ['RXRR']: # Simplified conditions for mock
                if probe_id not in cond_data[cond]: continue
                data = cond_data[cond][probe_id][:, local_idx, :]
                
                var_trace = np.var(data, axis=0, ddof=1)
                
                for interval in ['fx', 'pre', 'omit', 'post']:
                    if interval == 'fx':
                        start, end = WINDOWS['fx']
                    else:
                        start, end = WINDOWS[interval][cond]
                    
                    segment = data[:, start:end]
                    var_segment = var_trace[start:end]
                    
                    row[f'{cond}_{interval}_mean_fr'] = np.mean(segment) * 1000
                    
                    trial_isis = []
                    for t in range(segment.shape[0]):
                        spk_times = np.where(segment[t, :] == 1)[0]
                        if len(spk_times) > 1:
                            trial_isis.extend(np.diff(spk_times).tolist())
                    row[f'{cond}_{interval}_std_isi'] = np.std(trial_isis) if trial_isis else 0
                    
                    row[f'{cond}_{interval}_mean_var'] = np.mean(var_segment)
                    row[f'{cond}_{interval}_std_var'] = np.std(var_segment)
            
            all_rows.append(row)

    df = pd.DataFrame(all_rows)
    mock_output_csv_path = 'checkpoints/mock_omission_neurons_r_factors.csv'
    df.to_csv(mock_output_csv_path, index=False)
    print(f"
  Mock 48-factor matrix saved to {mock_output_csv_path}")
    print(f"
--- First 5 rows of mock output CSV:
{df.head().to_markdown(index=False)}")

    # Clean up mock files and directories
    import shutil
    shutil.rmtree('data/nwb')
    shutil.rmtree('data/arrays')
    os.remove(mock_layer_csv_path)
    print("
  Cleaned up mock environment.")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_extract_factors()
```