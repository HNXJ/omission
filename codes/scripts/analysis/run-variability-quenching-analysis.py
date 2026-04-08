
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

import os
import numpy as np
import pandas as pd
import h5py
from concurrent.futures import ProcessPoolExecutor
from codes.functions.spiking.neuro_variability_suite import NeuroVariabilitySuite, apply_post_hoc_smoothing
import json

# Parameters from Churchland 2010
WIN_SIZE = 50 # ms
STEP = 10 # ms
SIGMA_SMOOTH = 2.0 # for post-hoc smoothing

DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
NEURON_CAT_FILE = os.path.join(CHECKPOINT_DIR, "enhanced_neuron_categories.csv")

def process_session_spikes(session_id, neurons_df):
    """
    Computes MMFF for a single session across all probes and conditions.
    """
    session_neurons = neurons_df[neurons_df['session'] == int(session_id)]
    areas = session_neurons['area'].unique()
    
    results = {}
    
    # Conditions to process
    conditions = ["RRRR", "RXRR", "RRXR", "RRRX", "AAAB", "AAAX", "BBBA", "BBBX"]
    
    for area in areas:
        area_neurons = session_neurons[session_neurons['area'] == area]
        
        for cond in conditions:
            # Aggregate spike counts from all probes for this area
            all_counts = []
            
            probes = area_neurons['probe'].unique()
            for probe in probes:
                probe_area_neurons = area_neurons[area_neurons['probe'] == probe]
                unit_indices = probe_area_neurons['unit_idx'].values
                
                spk_file = os.path.join(DATA_DIR, f"ses{session_id}-units-probe{probe}-spk-{cond}.npy")
                if os.path.exists(spk_file):
                    spikes = np.load(spk_file) # (Trials, Neurons, Time)
                    # Filter for neurons in this area
                    spikes_area = spikes[:, unit_indices, :]
                    
                    counts, time_bins = NeuroVariabilitySuite.get_sliding_window_counts(spikes_area, win_size=WIN_SIZE, step=STEP)
                    all_counts.append(counts)
            
            if len(all_counts) > 0:
                # Concatenate along the Neuron axis
                combined_counts = np.concatenate(all_counts, axis=0)
                
                # Compute MMFF
                fano_trace = NeuroVariabilitySuite.compute_mmff(combined_counts)
                
                # Apply post-hoc smoothing
                fano_trace_smooth = apply_post_hoc_smoothing(fano_trace, sigma=SIGMA_SMOOTH)
                
                key = f"{area}_{cond}"
                if key not in results:
                    results[key] = []
                results[key].append({
                    'session': session_id,
                    'fano': fano_trace_smooth.tolist(),
                    'time_bins': (time_bins + WIN_SIZE/2).tolist() # Center of window
                })
                
    return results

def process_session_lfp(session_id):
    """
    Computes across-trial variance for continuous LFP signals.
    """
    h5_file = os.path.join(DATA_DIR, f"lfp_by_area_ses-{session_id}.h5")
    if not os.path.exists(h5_file):
        return {}
    
    results = {}
    with h5py.File(h5_file, 'r') as f:
        for area_name in f.keys():
            area_group = f[area_name]
            for cond in area_group.keys():
                data = area_group[cond][:] # (Channels, Trials, Time)
                
                # Compute Across-trial Variance
                var_trace = NeuroVariabilitySuite.compute_continuous_variability(data, sigma_smooth=SIGMA_SMOOTH)
                
                # var_trace shape: (Channels, Time)
                # Take the mean across channels to get an area-level trace
                avg_var_trace = np.mean(var_trace, axis=0)
                
                key = f"{area_name}_{cond}"
                if key not in results:
                    results[key] = []
                results[key].append({
                    'session': session_id,
                    'variance': avg_var_trace.tolist()
                })
    return results

def main():
    neurons_df = pd.read_csv(NEURON_CAT_FILE)
    sessions = neurons_df['session'].unique().astype(str)
    
    print(f"Starting Variability Quenching Analysis for {len(sessions)} sessions...")
    
    # Process SPK and LFP in parallel
    spk_results_all = {}
    lfp_results_all = {}
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Spikes
        spk_futures = {executor.submit(process_session_spikes, ses, neurons_df): ses for ses in sessions}
        # LFP
        lfp_futures = {executor.submit(process_session_lfp, ses): ses for ses in sessions}
        
        for future in spk_futures:
            res = future.result()
            for key, val in res.items():
                if key not in spk_results_all:
                    spk_results_all[key] = []
                spk_results_all[key].extend(val)
        
        for future in lfp_futures:
            res = future.result()
            for key, val in res.items():
                if key not in lfp_results_all:
                    lfp_results_all[key] = []
                lfp_results_all[key].extend(val)

    # Save results
    output_file = os.path.join(CHECKPOINT_DIR, "variability_quenching_results.json")
    final_output = {
        'spk_mmff': spk_results_all,
        'lfp_variance': lfp_results_all,
        'parameters': {
            'win_size': WIN_SIZE,
            'step': STEP,
            'sigma_smooth': SIGMA_SMOOTH
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f)
        
    print(f"Analysis complete. Results saved to {output_file}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
