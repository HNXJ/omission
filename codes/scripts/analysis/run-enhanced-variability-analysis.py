
import os
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from functions.neuro_variability_suite import NeuroVariabilitySuite, apply_post_hoc_smoothing
import json

# Parameters
WIN_SIZE = 50 
STEP = 10 
SIGMA_SMOOTH = 2.0 

DATA_DIR = "D:/Analysis/Omission/local-workspace/data"
CHECKPOINT_DIR = "D:/Analysis/Omission/local-workspace/checkpoints"
NEURON_CAT_FILE = os.path.join(CHECKPOINT_DIR, "enhanced_neuron_categories.csv")

# BANDS for burst detection
BANDS = {
    'theta': (3, 8),
    'alpha': (8, 14),
    'beta': (13, 30),
    'gamma': (35, 80)
}

def process_session_variability(session_id, neurons_df):
    session_id = str(session_id)
    session_neurons = neurons_df[neurons_df['session'] == int(session_id)]
    areas = session_neurons['area'].unique()
    
    # Map probes to areas for this session from neurons_df
    probe_to_area = session_neurons.groupby('probe')['area'].first().to_dict()
    probes = list(probe_to_area.keys())
    
    results = {}
    conditions = ["RRRR", "RXRR", "RRXR", "RRRX", "AAAB", "AAAX", "BBBA", "BBBX"]
    
    for cond in conditions:
        for probe in probes:
            area = probe_to_area[probe]
            
            # 1. Spikes (MMFF)
            spk_file = os.path.join(DATA_DIR, f"ses{session_id}-units-probe{probe}-spk-{cond}.npy")
            if os.path.exists(spk_file):
                unit_indices = session_neurons[session_neurons['probe'] == probe]['unit_idx'].values
                spikes = np.load(spk_file)[:, unit_indices, :]
                
                counts, time_bins = NeuroVariabilitySuite.get_sliding_window_counts(spikes, win_size=WIN_SIZE, step=STEP)
                mmff = NeuroVariabilitySuite.compute_mmff(counts, repeats=10)
                mmff_smooth = apply_post_hoc_smoothing(mmff, sigma=SIGMA_SMOOTH)
                
                key_spk = f"spk_{area}_{cond}"
                if key_spk not in results: results[key_spk] = []
                results[key_spk].append({'val': mmff_smooth.tolist(), 'time': (time_bins + WIN_SIZE/2).tolist()})
            
            # 2. LFP (MMV and Burst Fano)
            lfp_file = os.path.join(DATA_DIR, f"ses{session_id}-probe{probe}-lfp-{cond}.npy")
            if os.path.exists(lfp_file):
                lfp_data = np.load(lfp_file, mmap_mode='r') # (Trials, Channels, Time)
                # Correct shape for compute_continuous_mmv: (Channels, Trials, Time)
                lfp_trans = np.transpose(lfp_data, (1, 0, 2))
                
                # MMV (Mean-Matched Variation)
                mmv = NeuroVariabilitySuite.compute_continuous_mmv(lfp_trans, win_size=WIN_SIZE, step=STEP, repeats=10)
                mmv_smooth = apply_post_hoc_smoothing(mmv, sigma=SIGMA_SMOOTH)
                
                key_mmv = f"lfp_mmv_{area}_{cond}"
                if key_mmv not in results: results[key_mmv] = []
                results[key_mmv].append({'val': mmv_smooth.tolist()})
                
                # Burst Fano Factor
                for band_name, band_range in BANDS.items():
                    # Detect bursts on a representative channel
                    bursts = NeuroVariabilitySuite.detect_bursts(lfp_data[:, 64, :], band=band_range)
                    # bursts shape: (Trials, Time)
                    # Treat as pseudo-spikes: (Trials, 1, Time)
                    bursts_3d = bursts[:, np.newaxis, :]
                    b_counts, _ = NeuroVariabilitySuite.get_sliding_window_counts(bursts_3d, win_size=WIN_SIZE, step=STEP)
                    b_fano = NeuroVariabilitySuite.compute_mmff(b_counts, repeats=10)
                    
                    key_burst = f"lfp_burst_{band_name}_{area}_{cond}"
                    if key_burst not in results: results[key_burst] = []
                    results[key_burst].append({'val': apply_post_hoc_smoothing(b_fano, sigma=SIGMA_SMOOTH).tolist()})
                    
    return results

def main():
    neurons_df = pd.read_csv(NEURON_CAT_FILE)
    sessions = neurons_df['session'].unique().astype(str)
    
    print(f"Starting Multi-scale Variability Analysis for {len(sessions)} sessions...")
    
    all_results = {}
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(process_session_variability, ses, neurons_df): ses for ses in sessions}
        for future in futures:
            res = future.result()
            for key, val in res.items():
                if key not in all_results: all_results[key] = []
                all_results[key].extend(val)
                
    output_file = os.path.join(CHECKPOINT_DIR, "enhanced_variability_results.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f)
        
    print(f"Enhanced Analysis complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
