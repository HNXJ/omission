"""
vflip2_mapping_v2.py: Spectrolaminar mapping based on vFLIP2 logic for ALL sessions.
Finds the Layer 4 crossover point using Alpha/Beta vs Gamma power.
Uses Sample 1000-6000 (after Stim 1 onset).
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.ndimage import gaussian_filter1d
import glob

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\LFP_Extractions'
FS = 1000.0
BANDS = {
    'alpha_beta': (8, 30),
    'gamma': (35, 80)
}

SESSION_PROBES = {
    '230629': ['0', '1'],
    '230630': ['0', '1', '2'],
    '230714': ['0', '1'],
    '230719': ['0', '1', '2'],
    '230720': ['0', '1'],
    '230721': ['0', '1'],
    '230816': ['0', '1', '2'],
    '230818': ['0', '1', '2'],
    '230823': ['0', '1', '2'],
    '230825': ['0', '1', '2'],
    '230830': ['0', '1', '2'],
    '230831': ['0', '1', '2'],
    '230901': ['0', '1', '2']
}

def compute_profiles(lfp_data):
    # Use samples 1000-6000 (as per user instruction)
    data = lfp_data[:, :, 1000:6000]
    n_chans = data.shape[1]
    
    profiles = {band: np.zeros(n_chans) for band in BANDS}
    for ch in range(n_chans):
        f, pxx = welch(data[:, ch, :], fs=FS, nperseg=512, axis=-1)
        mean_pxx = np.mean(pxx, axis=0)
        for b, (fmin, fmax) in BANDS.items():
            profiles[b][ch] = np.mean(mean_pxx[(f >= fmin) & (f <= fmax)])
            
    # Smoothing and Normalization
    for b in profiles:
        profiles[b] = gaussian_filter1d(profiles[b], sigma=2.0)
        profiles[b] /= (np.max(profiles[b]) + 1e-12)
        
    return profiles

def find_crossover(profiles):
    ab = profiles['alpha_beta']
    ga = profiles['gamma']
    diff = ga - ab
    crossover = np.nan
    for i in range(len(diff) - 1):
        if diff[i] > 0 and diff[i+1] < 0:
            crossover = i + 0.5
            break
    return crossover

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = []
    
    for sid, probes in SESSION_PROBES.items():
        print(f"Processing Session {sid}...")
        for pid in probes:
            # Use AAAB for mapping
            fpath = os.path.join(DATA_DIR, f'ses{sid}-probe{pid}-lfp-AAAB.npy')
            if not os.path.exists(fpath): continue
            
            try:
                lfp = np.load(fpath, mmap_mode='r')
                profiles = compute_profiles(lfp)
                crossover = find_crossover(profiles)
                summary.append(f"Session {sid}: Probe {pid}: Crossover at channel {crossover:.2f}")
                
                # Plot
                plt.figure(figsize=(5, 8))
                chans = np.arange(len(profiles['gamma']))
                plt.plot(profiles['alpha_beta'], chans, 'b', label='Alpha/Beta')
                plt.plot(profiles['gamma'], chans, 'r', label='Gamma')
                plt.axhline(crossover, color='k', ls='--')
                plt.gca().invert_yaxis()
                plt.title(f"vFLIP2: {sid} P{pid}")
                plt.legend()
                plt.savefig(os.path.join(OUTPUT_DIR, f"vflip2_{sid}_p{pid}.png"))
                plt.close()
            except Exception as e:
                print(f"  Error P{pid}: {e}")
                
    with open(os.path.join(OUTPUT_DIR, "vflip2_summary.txt"), "w") as f:
        f.write("\n".join(summary))
    print(f"Summary saved to {OUTPUT_DIR}/vflip2_summary.txt")

if __name__ == "__main__":
    main()
