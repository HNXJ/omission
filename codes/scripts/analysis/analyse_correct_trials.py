
import pandas as pd
from pynwb import NWBHDF5IO
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Create output directory
output_dir = Path('omission/outputs/psth_plots')
output_dir.mkdir(exist_ok=True)

# Load the unit profile CSV
unit_profile_path = Path('D:/drive/omission/outputs/unit_nwb_profile.csv')
units_df = pd.read_csv(unit_profile_path)

# --- Filter for "Good" and "Stable" units ---
good_stable_units_df = units_df[
    (units_df['quality'] == 1.0) &
    (units_df['presence_ratio'] >= 0.95) &
    (units_df['firing_rate'] >= 1.0)
]
print(f"Found {len(good_stable_units_df)} good and stable units.")

# --- Process the first 5 units ---
for index, unit_info in good_stable_units_df.head().iterrows():
    session_nwb = unit_info['session_nwb']
    unit_id = unit_info['unit_id_in_session']
    psth_plot_path = output_dir / f"unit_{unit_id}_psth.png"

    nwb_path = Path(f'D:/analysis/nwb/{session_nwb}')
    print(f"Processing NWB file: {nwb_path} for unit ID: {unit_id}")

    if nwb_path.exists():
        with NWBHDF5IO(str(nwb_path), 'r') as io:
            nwb = io.read()

            # --- Get spike times for the unit ---
            unit_spike_times = nwb.units['spike_times'][unit_id]

            # --- Get correct trials ---
            intervals = nwb.intervals['omission_glo_passive'].to_dataframe()
            correct_trials = intervals[intervals['correct'] == '1.0']
            
            if correct_trials.empty:
                print(f"No correct trials found for unit {unit_id}. Skipping.")
                continue

            # --- Create a PSTH ---
            psth_window = [-0.5, 1.0]  # seconds
            bin_size = 0.05  # seconds
            bins = np.arange(psth_window[0], psth_window[1] + bin_size, bin_size)
            psth = np.zeros(len(bins) - 1)

            for _, trial in correct_trials.iterrows():
                trial_start = trial['start_time']
                relative_spikes = unit_spike_times - trial_start
                spikes_in_window = relative_spikes[
                    (relative_spikes >= psth_window[0]) &
                    (relative_spikes < psth_window[1])
                ]
                psth += np.histogram(spikes_in_window, bins=bins)[0]

            psth = psth / len(correct_trials) / bin_size

            # --- Plot and save PSTH ---
            plt.figure()
            plt.bar(bins[:-1], psth, width=bin_size)
            plt.title(f'PSTH for Unit {unit_id}')
            plt.xlabel('Time from trial start (s)')
            plt.ylabel('Firing Rate (Hz)')
            plt.savefig(psth_plot_path)
            plt.close()
            print(f"Saved PSTH plot to: {psth_plot_path}")

    else:
        print(f"NWB file not found at: {nwb_path}")

print("Finished processing units.")
