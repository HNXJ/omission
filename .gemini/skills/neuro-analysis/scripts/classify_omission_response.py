
import numpy as np
import glob
import re
from collections import defaultdict
import argparse
import os

def classify_omission_neurons_strict(data_dir):
    """
    Loops through all neuron data to classify them as omission positive responsive
    using a strict "maximum peak" criterion.
    """
    all_spk_files = glob.glob(os.path.join(data_dir, '*-units-*-spk-*.npy'))
    
    grouped_files = defaultdict(list)
    for f in all_spk_files:
        match = re.search(r'ses(\d+)-units-probe(\d+)', f)
        if match:
            grouped_files[(match.group(1), match.group(2))].append(f)

    omission_positive_units = set()

    print(f"Found {len(grouped_files)} unique session-probe combinations in {data_dir}")

    for (session, probe), files in grouped_files.items():
        print(f"Processing Session {session}, Probe {probe}...")

        condition_files = {re.search(r'-spk-(.*)\.npy', f).group(1): f for f in files if re.search(r'-spk-(.*)\.npy', f)}
        
        try:
            if 'RRRR' not in condition_files:
                print("  - RRRR control file not found. Skipping.")
                continue
            
            control_data = np.load(condition_files['RRRR'], mmap_mode='r')
            num_units = control_data.shape[1]
        except (StopIteration, IndexError, ValueError, FileNotFoundError) as e:
            print(f"  - Could not load control data for Session {session}, Probe {probe}. Skipping. Error: {e}")
            continue

        win = {
            "fx": (0, 1000), "p1": (0, 531), "d1": (531, 1031),
            "p2": (1031, 1562), "d2": (1562, 2062),
            "p3": (2062, 2593), "d3": (2593, 3093),
            "p4": (3093, 3624)
        }
        om_win = {"p2_om": win["p2"], "p3_om": win["p3"], "p4_om": win["p4"]}

        def get_rate(data, unit_idx, window):
            if data.ndim != 3 or data.shape[0] == 0: return 0
            return np.mean(data[:, unit_idx, window[0]:window[1]]) * 1000

        for unit_idx in range(num_units):
            unit_id = (session, probe, unit_idx)
            is_omission_responsive = False

            if 'RXRR' in condition_files:
                om_data = np.load(condition_files['RXRR'], mmap_mode='r')
                rate_om = get_rate(om_data, unit_idx, om_win["p2_om"])
                rate_fx_ctrl = get_rate(control_data, unit_idx, win["fx"])
                rate_p1_ctrl = get_rate(control_data, unit_idx, win["p1"])
                rate_d1_ctrl = get_rate(control_data, unit_idx, win["d1"])
                if rate_om > rate_fx_ctrl and rate_om > rate_p1_ctrl and rate_om > rate_d1_ctrl:
                    is_omission_responsive = True

            if not is_omission_responsive and 'RRXR' in condition_files:
                om_data = np.load(condition_files['RRXR'], mmap_mode='r')
                rate_om = get_rate(om_data, unit_idx, om_win["p3_om"])
                preceding_rates = [
                    get_rate(control_data, unit_idx, win["fx"]), get_rate(control_data, unit_idx, win["p1"]),
                    get_rate(control_data, unit_idx, win["d1"]), get_rate(control_data, unit_idx, win["p2"]),
                    get_rate(control_data, unit_idx, win["d2"])
                ]
                if all(rate_om > r for r in preceding_rates):
                    is_omission_responsive = True
            
            if not is_omission_responsive and 'RRRX' in condition_files:
                om_data = np.load(condition_files['RRRX'], mmap_mode='r')
                rate_om = get_rate(om_data, unit_idx, om_win["p4_om"])
                preceding_rates = [
                    get_rate(control_data, unit_idx, win["fx"]), get_rate(control_data, unit_idx, win["p1"]),
                    get_rate(control_data, unit_idx, win["d1"]), get_rate(control_data, unit_idx, win["p2"]),
                    get_rate(control_data, unit_idx, win["d2"]), get_rate(control_data, unit_idx, win["p3"]),
                    get_rate(control_data, unit_idx, win["d3"])
                ]
                if all(rate_om > r for r in preceding_rates):
                    is_omission_responsive = True
            
            if is_omission_responsive:
                omission_positive_units.add(unit_id)

    return len(omission_positive_units)

def main():
    parser = argparse.ArgumentParser(description="Classify neurons as omission positive responsive (strict).")
    parser.add_argument('--data_dir', type=str, default='../assets/data', help='Directory containing the .npy spike data files.')
    args = parser.parse_args()

    omission_count = classify_omission_neurons_strict(args.data_dir)

    print("\n--- Strict Classification Results ---")
    print(f"Total 'omission positive responsive' neurons: {omission_count}")

if __name__ == '__main__':
    main()
