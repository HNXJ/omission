"""
photodiode_alignment_v1.py: Compares Photodiode signal from NWB with V1 PSTH from .npy.
Alignment: Code 101.0 at Sample 1000.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from pynwb import NWBHDF5IO

# Paths
NWB_PATH = r'D:\Analysis\Omission\local-workspace\data\sub-V198o_ses-230720_rec.nwb'
NPY_PATH = r'D:\Analysis\Omission\local-workspace\data\ses230720-units-probe0-spk-AAAB.npy'
OUTPUT_PATH = r'D:\Analysis\Omission\local-workspace\figures\photodiode_alignment_v1.png'

def extract_photodiode():
    print(f"Loading NWB from {NWB_PATH}...")
    with NWBHDF5IO(NWB_PATH, 'r', load_namespaces=True) as io:
        nwb = io.read()
        pd_ts = nwb.acquisition['photodiode_1_tracking']
        pd_data = pd_ts.data[:]
        pd_times = pd_ts.timestamps[:]
        
        df = nwb.intervals['omission_glo_passive'].to_dataframe()
        # Find Code 101.0 for condition 1.0
        mask = (df['task_condition_number'].astype(str).str.startswith('1.0')) & (df['codes'].astype(str).str.startswith('101'))
        aaab_trials = df[mask]
        trial_starts = aaab_trials['start_time'].values[:50]
        
        all_pd_slices = []
        for t_start in trial_starts:
            # 1.0 second buffer to match master_npy_export.py
            idx_start = np.searchsorted(pd_times, t_start - 1.0)
            idx_end = idx_start + 6000
            if idx_end < len(pd_data):
                all_pd_slices.append(pd_data[idx_start:idx_end])
        
        if not all_pd_slices:
            print("  Warning: No Code 101 trials found.")
            return np.zeros(6000)
        return np.mean(all_pd_slices, axis=0)

def plot():
    mean_pd = extract_photodiode()
    print(f"Loading V1 PSTH...")
    v1_data = np.load(NPY_PATH, mmap_mode='r')
    v1_psth = np.mean(np.mean(v1_data, axis=0), axis=0) * 1000
    
    from scipy.ndimage import gaussian_filter1d
    v1_psth = gaussian_filter1d(v1_psth, sigma=5.0)
    
    fig, ax1 = plt.subplots(figsize=(15, 7))
    time = np.arange(6000)
    ax1.plot(time, v1_psth, color='black', label='V1 PSTH (Hz)')
    ax1.set_xlabel("Sample (ms)")
    ax1.set_ylabel("Firing Rate (Hz)")
    
    ax2 = ax1.twinx()
    pd_norm = (mean_pd - np.min(mean_pd)) / (np.max(mean_pd) - np.min(mean_pd) + 1e-6)
    ax2.plot(time, 1 - pd_norm, color='red', alpha=0.6, label='Photodiode (Inverted)')
    ax2.set_ylabel("Photodiode (Normalized)")
    
    # Overlay Task Intervals (Stimulus: 531ms, Delay: 500ms)
    OFFSET = 1000 # p1 at 1000ms
    EVENTS = [('fx', -500, 0), ('p1', 0, 531), ('d1', 531, 1031), ('p2', 1031, 1562), ('d2', 1562, 2062), 
              ('p3', 2062, 2593), ('d3', 2593, 3093), ('p4', 3093, 3624), ('d4', 3624, 4124)]
    
    for name, start, end in EVENTS:
        s, e = start + OFFSET, end + OFFSET
        if name.startswith('p'):
            ax1.axvspan(s, e, color='orange', alpha=0.2)
            ax1.text((s+e)/2, ax1.get_ylim()[1]*0.9, name, ha='center', weight='bold')
        else:
            ax1.axvspan(s, e, color='gray', alpha=0.1)
            ax1.text((s+e)/2, ax1.get_ylim()[1]*0.9, name, ha='center')

    plt.title("V1 Alignment Check: p1 Onset (Code 101) at Sample 1000")
    ax1.grid(True, alpha=0.3)
    plt.savefig(OUTPUT_PATH)
    print(f"Plot saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    plot()
