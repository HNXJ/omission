
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

import os
import numpy as np
import pandas as pd
from scipy.signal import correlate
from concurrent.futures import ThreadPoolExecutor
import json

# Parameters
MAX_LAG = 100 
BIN_SIZE = 1 
FS = 1000 
OMIT_WINDOW = slice(4093, 4624) # P4 Omission window (3093-3624ms post-P1)

DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
NEURON_CAT_FILE = os.path.join(CHECKPOINT_DIR, "enhanced_neuron_categories.csv")

def compute_ccg(spk1, spk2, max_lag=100):
    """
    spk1, spk2: (Trials, Time) binary arrays
    Returns: ccg (2*max_lag + 1,)
    """
    n_trials = spk1.shape[0]
    lags = np.arange(-max_lag, max_lag + 1)
    ccg_accum = np.zeros(len(lags))
    
    for i in range(n_trials):
        # Cross-correlation for each trial
        c = correlate(spk1[i], spk2[i], mode='full')
        center = len(c) // 2
        ccg_accum += c[center - max_lag : center + max_lag + 1]
        
    return ccg_accum / n_trials

def process_session_ccg(session_id, neurons_df):
    session_id = int(session_id)
    session_neurons = neurons_df[neurons_df['session'] == session_id]
    
    v1_units = session_neurons[(session_neurons['area'] == 'V1') & (session_neurons['category'].str.contains('Omit-Pref'))]
    pfc_units = session_neurons[(session_neurons['area'] == 'PFC') & (session_neurons['category'].str.contains('Omit-Pref'))]
    
    if len(v1_units) == 0 or len(pfc_units) == 0:
        return None
        
    # Load spiking data for RRRX (P4 Omission)
    v1_file = os.path.join(DATA_DIR, f"ses{session_id}-units-probe{v1_probe}-spk-RRRX.npy")
    pfc_file = os.path.join(DATA_DIR, f"ses{session_id}-units-probe{pfc_probe}-spk-RRRX.npy")
    
    if not (os.path.exists(v1_file) and os.path.exists(pfc_file)):
        return None
        
    v1_spk_all = np.nan_to_num(np.load(v1_file))[:, v1_units['unit_idx'].values, OMIT_WINDOW]
    pfc_spk_all = np.nan_to_num(np.load(pfc_file))[:, pfc_units['unit_idx'].values, OMIT_WINDOW]
    
    results = []
    # Compute CCG for all pairs
    for i in range(v1_spk_all.shape[1]):
        for j in range(pfc_spk_all.shape[1]):
            ccg = compute_ccg(v1_spk_all[:, i, :], pfc_spk_all[:, j, :], max_lag=MAX_LAG)
            
            # Peak finding
            peak_lag = np.argmax(ccg) - MAX_LAG
            results.append({
                'session': session_id,
                'v1_unit': int(v1_units['unit_idx'].iloc[i]),
                'pfc_unit': int(pfc_units['unit_idx'].iloc[j]),
                'peak_lag': int(peak_lag),
                'peak_value': float(np.max(ccg))
            })
            
    return results

def main():
    neurons_df = pd.read_csv(NEURON_CAT_FILE)
    sessions = [230630, 230816, 230830]
    
    print(f"Starting V1-PFC Spike-Spike CCG analysis for {len(sessions)} sessions...")
    
    all_pairs = []
    for ses in sessions:
        res = process_session_ccg(ses, neurons_df)
        if res:
            all_pairs.extend(res)
            
    if not all_pairs:
        print("No pairs found.")
        return
        
    output_file = os.path.join(CHECKPOINT_DIR, "v1_pfc_spike_ccg_results.json")
    with open(output_file, 'w') as f:
        json.dump(all_pairs, f)
        
    summary_df = pd.DataFrame(all_pairs)
    summary_df.to_csv(os.path.join(CHECKPOINT_DIR, "v1_pfc_spike_ccg_summary.csv"), index=False)
    
    print(f"Analysis complete. Found {len(all_pairs)} pairs.")
    print(f"Average Peak Lag: {summary_df['peak_lag'].mean():.2f} ms (Positive = V1 triggers PFC; Negative = PFC triggers V1)")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
