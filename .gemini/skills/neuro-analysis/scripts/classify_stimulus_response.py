
import numpy as np
import glob
import re
from collections import defaultdict
import argparse
import os

def classify_neurons(data_dir):
    """
    Loops through all neuron data to classify them as stimulus positive or negative.
    """
    all_spk_files = glob.glob(os.path.join(data_dir, '*-units-*-spk-*.npy'))
    
    grouped_files = defaultdict(list)
    for f in all_spk_files:
        match = re.search(r'ses(\d+)-units-probe(\d+)', f)
        if match:
            session_id = match.group(1)
            probe_id = match.group(2)
            grouped_files[(session_id, probe_id)].append(f)

    stim_pos_count = 0
    stim_neg_count = 0

    print(f"Found {len(grouped_files)} unique session-probe combinations in {data_dir}")

    for (session, probe), files in grouped_files.items():
        print(f"Processing Session {session}, Probe {probe}...")
        
        all_trials_data = []
        for f in files:
            try:
                data = np.load(f, mmap_mode='r')
                if data.ndim == 3 and data.shape[0] > 0 and data.shape[2] == 6000:
                    all_trials_data.append(data)
                else:
                    print(f"  - Skipping file with invalid shape: {f} -> {data.shape}")
            except Exception as e:
                print(f"  - Could not load file {f}: {e}")

        if not all_trials_data:
            print(f"  - No valid data found for Session {session}, Probe {probe}. Skipping.")
            continue
            
        full_data = np.concatenate(all_trials_data, axis=0)
        num_units = full_data.shape[1]
        
        fx_window = (0, 1000)
        p1_window = (1000, 1531)
        
        for unit_idx in range(num_units):
            unit_data = full_data[:, unit_idx, :]
            fx_rate = np.mean(unit_data[:, fx_window[0]:fx_window[1]]) * 1000
            p1_rate = np.mean(unit_data[:, p1_window[0]:p1_window[1]]) * 1000
            
            if p1_rate > fx_rate:
                stim_pos_count += 1
            elif fx_rate > p1_rate:
                stim_neg_count += 1
                
    return stim_pos_count, stim_neg_count

def main():
    parser = argparse.ArgumentParser(description="Classify neurons as stimulus positive or negative.")
    parser.add_argument('--data_dir', type=str, default='../assets/data', help='Directory containing the .npy spike data files.')
    args = parser.parse_args()

    stim_positive, stim_negative = classify_neurons(args.data_dir)

    print("\n--- Classification Results ---")
    print(f"Total 'stimulus positive responsive' neurons: {stim_positive}")
    print(f"Total 'stimulus negative responsive' neurons: {stim_negative}")

if __name__ == '__main__':
    main()
