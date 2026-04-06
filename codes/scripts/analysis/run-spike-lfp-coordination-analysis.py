
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

import os
import numpy as np
import pandas as pd
import h5py
from concurrent.futures import ProcessPoolExecutor
from codes.functions.spike_lfp_coordination import get_band_phase, compute_spike_lfp_ppc_trace
import json

DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
NEURON_CAT_FILE = os.path.join(CHECKPOINT_DIR, "enhanced_neuron_categories.csv")

BANDS = {
    'theta': (3, 8),
    'alpha': (8, 14),
    'beta': (13, 30),
    'gamma': (35, 80)
}

WIN_SIZE = 250
STEP = 50

from concurrent.futures import ThreadPoolExecutor

def process_single_neuron(neuron, conditions, session_id, probe_lfp_phases):
    area = neuron['area']
    probe = neuron['probe']
    unit_idx = neuron['unit_idx']
    category = neuron['category']
    neuron_results = {}
    
    for cond in conditions:
        spk_file = os.path.join(DATA_DIR, f"ses{session_id}-units-probe{probe}-spk-{cond}.npy")
        if os.path.exists(spk_file):
            spikes_all = np.load(spk_file, mmap_mode='r')
            spikes = spikes_all[:, unit_idx, :] # (Trials, Time)
            
            # Check if we have LFP phases for this probe and condition
            if probe in probe_lfp_phases and cond in probe_lfp_phases[probe]:
                for band_name in BANDS.keys():
                    phase = probe_lfp_phases[probe][cond][band_name] # (Trials, Time)
                    
                    # Ensure trial count matches
                    min_trials = min(spikes.shape[0], phase.shape[0])
                    s_subset = spikes[:min_trials, :]
                    p_subset = phase[:min_trials, :]
                    
                    ppc_trace, time_bins = compute_spike_lfp_ppc_trace(s_subset, p_subset, win_size=WIN_SIZE, step=STEP)
                    key = f"{area}_{category}_{cond}_{band_name}"
                    neuron_results[key] = ppc_trace.tolist()
    return neuron_results

def process_session_coordination(session_id, neurons_df):
    session_id = str(session_id)
    neurons = neurons_df[neurons_df['session'] == int(session_id)]
    
    conditions = ["RRRR", "RRRX", "AAAB", "AAAX"]
    results = {}
    
    # Pre-compute LFP phases for each probe in the session
    probe_lfp_phases = {}
    probes = neurons['probe'].unique()
    
    for probe in probes:
        probe_lfp_phases[probe] = {}
        for cond in conditions:
            lfp_file = os.path.join(DATA_DIR, f"ses{session_id}-probe{probe}-lfp-{cond}.npy")
            if os.path.exists(lfp_file):
                # Shape: (Trials, Channels, Time)
                lfp_data = np.load(lfp_file, mmap_mode='r')
                # Use a representative channel (e.g., middle of probe)
                avg_lfp = lfp_data[:, 64, :] 
                
                probe_lfp_phases[probe][cond] = {}
                for band_name, band_range in BANDS.items():
                    probe_lfp_phases[probe][cond][band_name] = get_band_phase(avg_lfp, band_range)

    # Parallel processing of neurons
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_single_neuron, n, conditions, session_id, probe_lfp_phases) for _, n in neurons.iterrows()]
        for future in futures:
            n_res = future.result()
            for key, trace in n_res.items():
                if key not in results: results[key] = []
                results[key].append(trace)
                            
    final_results = {}
    for key, traces in results.items():
        traces = np.array(traces)
        final_results[key] = {
            'mean': np.nanmean(traces, axis=0).tolist(),
            'time_bins': np.arange(0, 6000 - WIN_SIZE + 1, STEP).tolist()
        }
    return final_results

def main():
    neurons_df = pd.read_csv(NEURON_CAT_FILE)
    # Filter for interesting neurons only to save time (e.g. Omit, Stim, etc)
    interesting_neurons = neurons_df[neurons_df['category'] != 'Other']
    sessions = interesting_neurons['session'].unique().astype(str)
    
    print(f"Starting Spike-LFP Coordination Analysis for {len(sessions)} sessions...")
    
    all_results = {}
    
    # Run sequentially for now to avoid memory overflow with large LFP arrays in parallel
    for ses in sessions:
        print(f"Processing session {ses}...")
        res = process_session_coordination(ses, interesting_neurons)
        # Merge results
        for key, val in res.items():
            if key not in all_results:
                all_results[key] = []
            all_results[key].append(val)
            
    # Aggregated results across sessions
    final_agg = {}
    for key, vals in all_results.items():
        # Aggregating the session-level means
        means = np.array([v['mean'] for v in vals])
        final_agg[key] = {
            'mean': np.nanmean(means, axis=0).tolist(),
            'time_bins': vals[0]['time_bins']
        }
        
    output_file = os.path.join(CHECKPOINT_DIR, "spike_lfp_coordination_results.json")
    with open(output_file, 'w') as f:
        json.dump(final_agg, f)
        
    print(f"Analysis complete. Results saved to {output_file}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
