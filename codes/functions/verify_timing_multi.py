"""
verify_timing_multi_v1.py: Validates timing consistency across all sessions with V1 data.
Plots population PSTHs for multiple sessions on a single axis.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from pathlib import Path

DATA_DIR = Path(__file__).parents[2] / "data"
OUTPUT_PATH = Path(__file__).parents[2] / "output" / "timing_verification_multi_v1.png"

# Mapping of Session ID to Probe ID that contains V1/V2
V1_MAPPING = {
    '230629': '0',
    '230630': '1',
    '230714': '0',
    '230719': '1',
    '230720': '0',
    '230721': '0',
    '230816': '1',
    '230823': '2',
    '230830': '1'
}

# Task Timing (531ms stim / 500ms delay)
EVENTS = [
    ('fx', -500, 0),
    ('p1', 0, 531),
    ('d1', 531, 1031),
    ('p2', 1031, 1562),
    ('d2', 1562, 2062),
    ('p3', 2062, 2593),
    ('d3', 2593, 3093),
    ('p4', 3093, 3624),
    ('d4', 3624, 4124)
]

def plot_multi_v1():
    plt.figure(figsize=(15, 10))
    
    # Hypothesis: p1 onset is at Sample 1000 (1.0s pre-stim)
    OFFSET = 1000
    time = np.arange(6000)
    
    # Overlay Task Intervals
    for name, start, end in EVENTS:
        s, e = start + OFFSET, end + OFFSET
        if name.startswith('p'):
            plt.axvspan(s, e, color='orange', alpha=0.1)
            plt.text((s+e)/2, 0, name, ha='center', weight='bold', color='orange', alpha=0.5)
        elif name == 'fx':
            plt.axvspan(s, e, color='blue', alpha=0.05)
    
    # Loop through sessions
    for sid, pid in V1_MAPPING.items():
        fname = f'ses{sid}-units-probe{pid}-spk-AAAB.npy'
        fpath = os.path.join(DATA_DIR, fname)
        if not os.path.exists(fpath): continue
        
        print(f"  Processing Session {sid}...")
        try:
            data = np.load(fpath, mmap_mode='r')
            pop_psth = np.mean(np.mean(data, axis=0), axis=0) * 1000
            pop_psth_smooth = gaussian_filter1d(pop_psth, sigma=15.0)
            plt.plot(time, pop_psth_smooth, label=f"Ses {sid}", alpha=0.8)
        except: pass

    plt.title("Timing Verification: V1 Sessions (AAAB Condition)\nStimulus: 531ms | Delay: 500ms | Alignment: p1 onset at 1000ms")
    plt.xlabel("Sample Index (ms)")
    plt.ylabel("Population Firing Rate (Hz)")
    plt.axvline(OFFSET, color='red', linestyle='--', label='Predicted p1 Onset (1000ms)')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0))
    plt.xlim(0, 6000)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH)
    print(f"\nMulti-session plot saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    plot_multi_v1()
