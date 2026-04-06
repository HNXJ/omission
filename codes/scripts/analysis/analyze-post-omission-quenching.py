
from codes.config.paths import DATA_DIR, PROCESSED_DATA_DIR

import os
import numpy as np
import pandas as pd
import h5py
from codes.functions.neuro_variability_suite import NeuroVariabilitySuite, apply_post_hoc_smoothing
import json

# Parameters
WIN_SIZE = 50 
STEP = 10 
SIGMA_SMOOTH = 2.0 

DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
NEURON_CAT_FILE = os.path.join(CHECKPOINT_DIR, "enhanced_neuron_categories.csv")

# Post-Omission Windows
# P3 starts at 2062ms, P4 starts at 3093ms
P3_WINDOW = (2062, 2062 + 531)
P4_WINDOW = (3093, 3093 + 531)

from concurrent.futures import ProcessPoolExecutor

def process_session(ses, neurons_df, comparisons):
    session_neurons = neurons_df[neurons_df['session'] == int(ses)]
    areas = session_neurons['area'].unique()
    session_results = {}
    
    for area in areas:
        area_neurons = session_neurons[session_neurons['area'] == area]
        probes = area_neurons['probe'].unique()
        unit_indices_per_probe = {p: area_neurons[area_neurons['probe'] == p]['unit_idx'].values for p in probes}
        
        for cond_omit, cond_std, stim_pos in comparisons:
            counts_omit = []
            counts_std = []
            
            for probe in probes:
                unit_indices = unit_indices_per_probe[probe]
                omit_file = os.path.join(DATA_DIR, f"ses{ses}-units-probe{probe}-spk-{cond_omit}.npy")
                std_file = os.path.join(DATA_DIR, f"ses{ses}-units-probe{probe}-spk-{cond_std}.npy")
                
                if os.path.exists(omit_file) and os.path.exists(std_file):
                    spk_omit = np.load(omit_file)[:, unit_indices, :]
                    spk_std = np.load(std_file)[:, unit_indices, :]
                    c_omit, time_bins = NeuroVariabilitySuite.get_sliding_window_counts(spk_omit, win_size=WIN_SIZE, step=STEP)
                    c_std, _ = NeuroVariabilitySuite.get_sliding_window_counts(spk_std, win_size=WIN_SIZE, step=STEP)
                    counts_omit.append(c_omit)
                    counts_std.append(c_std)
            
            if len(counts_omit) > 0:
                combined_omit = np.concatenate(counts_omit, axis=0)
                combined_std = np.concatenate(counts_std, axis=0)
                mmff_omit = NeuroVariabilitySuite.compute_mmff(combined_omit, repeats=10)
                mmff_std = NeuroVariabilitySuite.compute_mmff(combined_std, repeats=10)
                
                key = f"{area}_{cond_omit}_vs_{cond_std}_{stim_pos}"
                if key not in session_results:
                    session_results[key] = []
                session_results[key].append({
                    'session': ses,
                    'mmff_omit': mmff_omit.tolist(),
                    'mmff_std': mmff_std.tolist(),
                    'time_bins': (time_bins + WIN_SIZE/2).tolist()
                })
    return session_results

def run_post_omit_comparison():
    neurons_df = pd.read_csv(NEURON_CAT_FILE)
    sessions = neurons_df['session'].unique().astype(str)
    
    comparisons = [
        ("AXAB", "AAAB", "P3"),
        ("AAXB", "AAAB", "P4"),
        ("BXBA", "BBBA", "P3"),
        ("BBXA", "BBBA", "P4"),
        ("RXRR", "RRRR", "P3"),
        ("RRXR", "RRRR", "P4")
    ]
    
    results = {}
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_session, ses, neurons_df, comparisons) for ses in sessions]
        for future in futures:
            session_results = future.result()
            for key, val in session_results.items():
                if key not in results:
                    results[key] = []
                results[key].extend(val)
    
    output_file = os.path.join(CHECKPOINT_DIR, "post_omission_quenching_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f)
    print(f"Post-omission quenching analysis complete. Results saved to {output_file}")
                    
    # Save results
    output_file = os.path.join(CHECKPOINT_DIR, "post_omission_quenching_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f)
    print(f"Post-omission quenching analysis complete. Results saved to {output_file}")


def main(args=None):
    run_post_omit_comparison()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
