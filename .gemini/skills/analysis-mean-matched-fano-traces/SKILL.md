---
name: analysis-mean-matched-fano-traces
description: Computes the Mean-Matched Fano Factor (MMFF) for neural spiking data across different brain areas and experimental conditions. This skill is crucial for normalizing and analyzing neuronal variability while controlling for differences in mean firing rates, providing insights into the stability and precision of neural coding in response to stimuli or during cognitive tasks.
---
# SKILL: analysis-mean-matched-fano-traces

## Description
This skill focuses on computing the Mean-Matched Fano Factor (MMFF), a robust metric for analyzing the variability of neural firing rates. The MMFF method normalizes the Fano Factor (variance/mean spike count) by statistically matching the mean firing rates across different conditions or brain areas. This ensures that observed differences in variability are not merely artifacts of differences in mean activity. The skill processes NWB electrode information to map units to specific brain regions, extracts spike data from corresponding NumPy files, and calculates MMFF in sliding time windows, ultimately providing smoothed traces of variability for comparative analysis.

## Core Tasks
1.  **`get_unit_to_area_map(nwb_path)`**:
    *   **Purpose**: Maps individual neural units to their assigned brain regions based on NWB electrode metadata.
    *   **Inputs**: Path to an NWB (.nwb) file.
    *   **Outputs**: A dictionary mapping `(probe_id, local_unit_idx)` to the assigned brain area (e.g., 'V1', 'PFC').
2.  **`compute_mmff()`**:
    *   **Purpose**: Orchestrates the MMFF computation across multiple sessions, conditions, and brain areas.
    *   **Inputs**:
        *   NWB (.nwb) files located in `data/nwb/`.
        *   Neural spike data as NumPy (.npy) files (e.g., `data/arrays/ses<ID>-units-probe<ID>-spk-<COND>.npy`).
        *   Configuration parameters for window size (`WIN_SIZE`), step size (`STEP`), and brain area ordering (`AREA_ORDER`, `AREA_MAPPING`).
    *   **Process**:
        *   Collects spike count means and variances in sliding windows for all units.
        *   Applies a mean-matching algorithm to equalize mean firing rate distributions.
        *   Calculates the Fano Factor (variance/mean) for the mean-matched distributions.
        *   Applies Gaussian smoothing to the resulting Fano Factor traces.
    *   **Outputs**: A JSON file (`checkpoints/area_mmff_traces.json`) containing the smoothed MMFF traces for each brain area and condition.

## Inputs
*   **NWB Files**: Located in `data/nwb/`, containing electrode location and unit metadata.
*   **Spike Data Files**: NumPy arrays (`.npy`) in `data/arrays/` named like `ses<session_id>-units-probe<probe_id>-spk-<condition>.npy`, where each array contains spike times or binned spike counts.
*   **Configuration**: Internal parameters within the script, such as `WIN_SIZE` (window for spike counting), `STEP` (step for sliding window), `AREA_ORDER` (list of brain areas), `AREA_MAPPING` (mapping for raw electrode labels).

## Outputs
*   **`checkpoints/area_mmff_traces.json`**: A JSON file storing a dictionary where keys are brain areas, and values are dictionaries of conditions, each containing a list of smoothed Mean-Matched Fano Factor values over time.

## Example Use

```python
import numpy as np
import pandas as pd
import os
from pynwb import NWBHDF5IO
from collections import defaultdict
import re
import json
from scipy.ndimage import gaussian_filter1d
from types import SimpleNamespace # For mocking NWB objects

# --- Mocking constants and helper functions from compute_mean_matched_fano.py ---
AREA_ORDER = ['V1', 'PFC'] # Simplified for example
CHANNELS_PER_PROBE = 128
AREA_MAPPING = {} # Simplified for example
WIN_SIZE = 150 
STEP = 5 

def mock_get_unit_to_area_map(nwb_path, session_id):
    # Simulate unit to area mapping based on session ID
    unit_map = {}
    if session_id == "230629":
        # Mocking 2 units for probe 0, one in V1, one in PFC
        unit_map[(0, 0)] = 'V1' 
        unit_map[(0, 1)] = 'PFC'
    return unit_map

# --- Mocking the compute_mmff function ---
def mock_compute_mmff():
    print("--- Demonstrating Mean-Matched Fano Factor Computation (Mock) ---")
    
    # Create mock NWB files and spike data directories if they don't exist
    os.makedirs('data/nwb', exist_ok=True)
    os.makedirs('data/arrays', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)

    # Simulate NWB files and spike .npy files for two sessions
    mock_sessions = ["230629", "230630"]
    mock_conditions = ['RRRR', 'RXRR'] # Simplified conditions

    for session_id in mock_sessions:
        # Create dummy NWB file
        with open(f'data/nwb/sub-mock_ses-{session_id}_rec.nwb', 'w') as f:
            f.write("mock nwb content") # Content doesn't matter for mock NWBHDF5IO
        
        # Create dummy spike .npy files for probe 0, 2 units
        for cond in mock_conditions:
            # Simulate (trials, units, time_bins)
            # Example: 10 trials, 2 units, 6000 time bins
            mock_spike_data = np.random.poisson(lam=0.5, size=(10, 2, 6000)) 
            np.save(f'data/arrays/ses{session_id}-units-probe0-spk-{cond}.npy', mock_spike_data)
            
    # Mock glob.glob behavior
    mock_nwb_files = [f'data/nwb/sub-mock_ses-{s}_rec.nwb' for s in mock_sessions]
    
    time_bins = np.arange(0, 6000 - WIN_SIZE, STEP)
    stats = {area: {cond: {t: {'m': [], 'v': []} for t in time_bins} 
                    for cond in mock_conditions} 
             for area in AREA_ORDER}

    for nwb_path in mock_nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"  Collecting mean/var stats for mock session {session_id}...")
        u_map = mock_get_unit_to_area_map(nwb_path, session_id) # Use mock map
        
        for cond in mock_conditions:
            mock_spk_files = [f'data/arrays/ses{session_id}-units-probe0-spk-{cond}.npy']
            for f in mock_spk_files: # Only one mock file for simplicity
                p_id = 0 # Mock probe ID
                data = np.load(f, mmap_mode='r')
                for u_idx in range(data.shape[1]): # Iterate mock units
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

    print("\n  Applying Mean-Matching across all mock areas...")
    final_results = {area: {cond: [] for cond in stats[area]} for area in AREA_ORDER}

    for area in AREA_ORDER:
        for cond in stats[area]:
            all_means = []
            for t in time_bins:
                all_means.extend(stats[area][cond][t]['m'])
            
            if not all_means: continue
            
            hist_bins = np.linspace(0, max(all_means) + 1, 10) # Simplified hist_bins
            global_counts, _ = np.histogram(all_means, bins=hist_bins)
            global_counts_norm = global_counts / (np.sum(global_counts) or 1) # Avoid division by zero

            trace = []
            for t in time_bins:
                ms = np.array(stats[area][cond][t]['m'])
                vs = np.array(stats[area][cond][t]['v'])
                
                if len(ms) < 2: # Reduced threshold for mock data
                    trace.append(np.nan)
                    continue

                current_counts, _ = np.histogram(ms, bins=hist_bins)
                valid = (current_counts > 0) & (global_counts_norm > 0)
                scale = np.min(current_counts[valid] / global_counts_norm[valid]) if any(valid) else 0
                
                matched_ms = []
                matched_vs = []
                
                for i in range(len(hist_bins)-1):
                    idx = np.where((ms >= hist_bins[i]) & (ms < hist_bins[i+1]))[0]
                    n_needed = int(np.floor(global_counts_norm[i] * scale))
                    if len(idx) > 0 and n_needed > 0:
                        chosen = np.random.choice(idx, min(n_needed, len(idx)), replace=False)
                        matched_ms.extend(ms[chosen])
                        matched_vs.extend(vs[chosen])
                
                if len(matched_ms) > 1: # Reduced threshold for mock data
                    fano = np.mean(np.array(matched_vs) / np.array(matched_ms))
                    trace.append(fano)
                else:
                    trace.append(np.mean(vs/ms) if len(ms)>0 else np.nan)

            # --- Post-hoc Gaussian Smoothing ---
            trace = np.array(trace)
            nan_mask = np.isnan(trace)
            if not np.all(nan_mask):
                valid_idx = np.where(~nan_mask)[0]
                if len(valid_idx) > 1:
                    trace[nan_mask] = np.interp(np.where(nan_mask)[0], valid_idx, trace[valid_idx])
                elif len(valid_idx) == 1:
                    trace[nan_mask] = trace[valid_idx[0]] # Fill with single valid point
                else:
                    trace[:] = np.nan # If no valid points, all remain nan
                
                trace = gaussian_filter1d(trace, sigma=5.0, mode='nearest') # Use nearest to handle edges with NaNs
                trace[nan_mask] = np.nan # Re-apply NaNs
            
            final_results[area][cond] = list(trace)

    # Ensure checkpoints directory exists for the mock run
    os.makedirs('checkpoints', exist_ok=True)
    
    # The actual file saves to 'checkpoints/area_mmff_traces.json'
    mock_output_path = 'checkpoints/mock_area_mmff_traces.json'
    serializable = {area: {cond: final_results[area][cond] for cond in final_results[area]} for area in final_results}
    with open(mock_output_path, 'w') as f:
        json.dump(serializable, f, indent=4)
    
    print(f"\n  Stabilized MMFF traces (mock) saved to {mock_output_path}")
    print(f"  Example V1 RRRR trace segment: {serializable['V1']['RRRR'][:5]}")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_compute_mmff()
    
    # Cleanup mock files (optional)
    # import shutil
    # shutil.rmtree('data/nwb')
    # shutil.rmtree('data/arrays')
    # shutil.rmtree('checkpoints')
