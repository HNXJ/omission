"""
verify_timing_v1.py: Validates the alignment of the 6000ms data window.
Plots V1 population PSTH and overlays task events to confirm T=0 alignment.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
FILE = os.path.join(DATA_DIR, 'ses230720-units-probe0-spk-AAAB.npy') # V1/V2 Probe
OUTPUT_PATH = r'D:\Analysis\Omission\local-workspace\figures\timing_verification_v1.png'

# Task Timing from TASK_DETAILS.md (relative to p1 onset = 0)
EVENTS = [
    ('fx', -500, 0),
    ('p1', 0, 500),
    ('d1', 500, 1031),
    ('p2', 1031, 1531),
    ('d2', 1531, 2062),
    ('p3', 2062, 2562),
    ('d3', 2562, 3093),
    ('p4', 3093, 3593),
    ('d4', 3593, 4124)
]

def plot_verification():
    print(f"Loading data from {FILE}...")
    # Shape: (Trials, Units, Samples)
    data = np.load(FILE, mmap_mode='r')
    n_trials, n_units, n_samples = data.shape
    
    # Calculate population PSTH (average across trials and units)
    # Binary spikes -> Sum over units -> Mean over trials -> Gaussian smooth
    pop_psth = np.mean(np.mean(data, axis=0), axis=0) * 1000 # Convert to Hz
    
    # Gaussian smoothing
    from scipy.ndimage import gaussian_filter1d
    pop_psth_smooth = gaussian_filter1d(pop_psth, sigma=10.0)
    
    plt.figure(figsize=(15, 7))
    time = np.arange(n_samples)
    
    # Plot Neural Activity
    plt.plot(time, pop_psth_smooth, color='black', linewidth=2, label='V1 Population FR (Hz)')
    
    # Hypothesis: T=0 (p1 onset) is at sample 2000 (2000ms pre-stim)
    # We will plot two sets of event lines: one starting at 1000, one at 2000
    OFFSET_HYPOTHESIS = 2000 
    
    colors = ['#FF9999', '#99FF99', '#9999FF', '#FFFF99', '#FF99FF']
    
    for i, (name, start, end) in enumerate(EVENTS):
        s_idx = start + OFFSET_HYPOTHESIS
        e_idx = end + OFFSET_HYPOTHESIS
        
        # Draw background patch for stim periods
        if name.startswith('p'):
            plt.axvspan(s_idx, e_idx, color='orange', alpha=0.2)
            plt.text((s_idx+e_idx)/2, plt.ylim()[1]*0.9, name, ha='center', fontweight='bold')
        else:
            plt.axvspan(s_idx, e_idx, color='gray', alpha=0.1)
            plt.text((s_idx+e_idx)/2, plt.ylim()[1]*0.9, name, ha='center')

    plt.title(f"Timing Verification: V1 Population Activity (Session 230720)\nHypothesis: Stim 1 Onset at Sample {OFFSET_HYPOTHESIS}")
    plt.xlabel("Sample Index (ms)")
    plt.ylabel("Firing Rate (Hz)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH)
    print(f"Plot saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    plot_verification()
