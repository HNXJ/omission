import h5py
import numpy as np
import matplotlib.pyplot as plt

# --- Config ---
INPUT_H5 = r'D:\OmissionAnalysis\spikes_by_condition_ses-230818.h5'
TARGET_CONDITION = 'AAAB'
OUTPUT_PNG = r'D:/OmissionAnalysis/timing_validation_plot.png'

# Event timings relative to Stimulus 1 onset (t=0) in seconds
# Stimuli are ~1000ms apart
EVENT_TIMESTAMPS = {
    "Fixation": -0.5,
    "Stim 1 (t=0)": 0.0,
    "Stim 2": 1.0,
    "Stim 3": 2.0,
    "Stim 4": 3.0 
}

# --- Main ---
with h5py.File(INPUT_H5, 'r') as f:
    if TARGET_CONDITION not in f:
        print(f"Condition '{TARGET_CONDITION}' not found.")
    else:
        # Load spiking data [trials, units, time]
        spikes = f[f'{TARGET_CONDITION}/spiking_activity'][()]
        
        # 1. Average across trials to get [units, time]
        mean_unit_activity = np.mean(spikes, axis=0)
        
        # 2. Average across units to get [time] (Population Average)
        population_average = np.mean(mean_unit_activity, axis=0)
        
        # 3. Smooth with a 50ms Gaussian kernel for visualization
        from scipy.ndimage import gaussian_filter1d
        smoothed_avg = gaussian_filter1d(population_average * 1000, sigma=50) # Convert to Hz
        
        # 4. Create Time Axis (-1s to +5s relative to Stim 1)
        time_axis = np.linspace(-1000, 5000, 6000)

        # 5. Plot
        plt.figure(figsize=(15, 7))
        plt.plot(time_axis, smoothed_avg, color='#CFB87C', label=f'Population Average ({TARGET_CONDITION})')
        
        # Add event markers
        for event, ts in EVENT_TIMESTAMPS.items():
            plt.axvline(ts * 1000, color='cyan', linestyle='--', alpha=0.7, label=event)
            
        plt.xlabel("Time from Stimulus 1 Onset (ms)")
        plt.ylabel("Population Firing Rate (Hz, smoothed)")
        plt.title(f"Corrected Timing Validation: Population Firing Rate (Session 230818, N={spikes.shape[1]} units)")
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.xlim(-1000, 4000)
        
        plt.savefig(OUTPUT_PNG)
        print(f"Corrected timing validation plot saved to {OUTPUT_PNG}")
