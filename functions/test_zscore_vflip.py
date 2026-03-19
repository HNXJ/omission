"""
test_zscore_vflip.py: Comparison of max-norm vs z-score for vFLIP2 mapping.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.ndimage import gaussian_filter1d

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
FILE = os.path.join(DATA_DIR, 'ses230831-probe1-lfp-BBBA.npy')
BANDS = {'alpha_beta': (8, 30), 'gamma': (35, 80)}

def analyze():
    print(f"Loading {FILE}...")
    lfp = np.load(FILE, mmap_mode='r')
    data = lfp[:, :, 1000:6000]
    n_chans = data.shape[1]
    
    profiles = {band: np.zeros(n_chans) for band in BANDS}
    for ch in range(n_chans):
        f, pxx = welch(data[:, ch, :], fs=1000, nperseg=512, axis=-1)
        mean_pxx = np.mean(pxx, axis=0)
        for band, (f_min, f_max) in BANDS.items():
            profiles[band][ch] = np.mean(mean_pxx[(f >= f_min) & (f <= f_max)])
            
    # Smoothing
    for b in profiles: profiles[b] = gaussian_filter1d(profiles[b], sigma=2.0)
    
    # Max-norm
    ab_max = profiles['alpha_beta'] / np.max(profiles['alpha_beta'])
    ga_max = profiles['gamma'] / np.max(profiles['gamma'])
    
    # Z-norm
    ab_z = (profiles['alpha_beta'] - np.mean(profiles['alpha_beta'])) / np.std(profiles['alpha_beta'])
    ga_z = (profiles['gamma'] - np.mean(profiles['gamma'])) / np.std(profiles['gamma'])
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 8), sharey=True)
    chans = np.arange(n_chans)
    
    ax1.plot(ab_max, chans, 'b', label='Alpha/Beta')
    ax1.plot(ga_max, chans, 'r', label='Gamma')
    ax1.set_title("Max-Norm")
    ax1.invert_yaxis()
    ax1.legend()
    
    ax2.plot(ab_z, chans, 'b', label='Alpha/Beta')
    ax2.plot(ga_z, chans, 'r', label='Gamma')
    ax2.set_title("Z-Score Norm")
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(r'D:\Analysis\Omission\local-workspace\LFP_Extractions\zscore_comparison.png')
    print("Comparison plot saved to LFP_Extractions/zscore_comparison.png")

if __name__ == "__main__":
    analyze()
