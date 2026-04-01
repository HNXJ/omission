"""
vflip2_mapping.py: Spectrolaminar mapping based on vFLIP2 logic.
Finds the Layer 4 crossover point by comparing Alpha/Beta and Gamma power profiles.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.ndimage import gaussian_filter1d
import glob

# Configuration
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\LFP_Extractions'
FS = 1000.0
BANDS = {
    'alpha_beta': (8, 30),
    'gamma': (35, 80)
}
CHANNEL_SPACING = 0.04  # 40um

def compute_spectrolaminar_profiles(lfp_data, fs=1000.0):
    """
    Computes depth-resolved power profiles for Alpha/Beta and Gamma.
    lfp_data: (Trials, Channels, Samples)
    """
    # Use samples 1000-6000 as per user instruction
    data = lfp_data[:, :, 1000:6000]
    n_trials, n_chans, n_samples = data.shape
    
    # Compute PSD for each trial and channel
    # We can average across trials first to save computation if linearity holds, 
    # but Welch's on each trial and then averaging PSDs is more robust.
    
    psd_profiles = {band: np.zeros(n_chans) for band in BANDS}
    
    # Flatten trials and channels for batch processing or loop
    # For memory efficiency, we process channel by channel
    print(f"  Computing PSD for {n_chans} channels...")
    for ch in range(n_chans):
        ch_data = data[:, ch, :] # (Trials, Samples)
        f, pxx = welch(ch_data, fs=fs, nperseg=512, axis=-1)
        # Average PSD across trials
        mean_pxx = np.mean(pxx, axis=0)
        
        # Integrate power in bands
        for band_name, (f_min, f_max) in BANDS.items():
            mask = (f >= f_min) & (f <= f_max)
            psd_profiles[band_name][ch] = np.mean(mean_pxx[mask])
            
    # Normalize profiles between 0 and 1 for easier crossover detection
    # but maybe we should use a relative power approach.
    # vFLIP2 logic often uses relative power normalized by max at each frequency.
    # Here we follow the senior expert's simpler logic: compare the two bands.
    
    # Spatial smoothing across electrodes
    for band_name in psd_profiles:
        psd_profiles[band_name] = gaussian_filter1d(psd_profiles[band_name], sigma=2.0)
        
    return psd_profiles

def find_crossover(profiles):
    """
    Finds the crossover point where Gamma power begins to dominate Alpha/Beta.
    Assuming P0 is top (superficial) and P127 is bottom (deep).
    Gamma is higher in superficial, Alpha/Beta higher in deep.
    So we look for where Gamma > Alpha/Beta (moving from top to bottom) 
    or where Alpha/Beta > Gamma (moving from bottom to top).
    Standard vFLIP2: Deep is Alpha/Beta, Superficial is Gamma.
    """
    ab = profiles['alpha_beta']
    ga = profiles['gamma']
    
    # Normalize both to their max to handle different power scales
    ab_norm = ab / (np.max(ab) + 1e-12)
    ga_norm = ga / (np.max(ga) + 1e-12)
    
    # Find the intersection
    diff = ga_norm - ab_norm
    
    # Moving from top (0) to bottom (127), Gamma should be higher in superficial, 
    # then cross over so Alpha/Beta is higher in deep.
    # So we look for a zero-crossing from positive to negative.
    
    crossover_idx = np.nan
    for i in range(len(diff) - 1):
        if diff[i] > 0 and diff[i+1] < 0:
            crossover_idx = i + 0.5 # Interpolated
            break
            
    return crossover_idx, ab_norm, ga_norm

def process_session(session_id, probes):
    print(f"\n>>> Processing Session: {session_id}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    results = {}
    
    for probe in probes:
        # Load one condition to find the crossover (e.g., AAAB or RRRR)
        # We'll use RRXR if available as it's a random variant, or just pick the first one
        files = glob.glob(os.path.join(DATA_DIR, f'ses{session_id}-probe{probe}-lfp-*.npy'))
        if not files:
            print(f"  No LFP files found for session {session_id} probe {probe}")
            continue
            
        # Use a high-trial condition for better SNR, e.g., BBBA or AAAB
        best_file = None
        for f in files:
            if 'BBBA' in f: best_file = f; break
        if not best_file: best_file = files[0]
        
        print(f"  Analyzing {os.path.basename(best_file)} for mapping...")
        lfp_data = np.load(best_file, mmap_mode='r')
        
        profiles = compute_spectrolaminar_profiles(lfp_data)
        crossover, ab_norm, ga_norm = find_crossover(profiles)
        
        results[probe] = {
            'crossover': crossover,
            'ab_norm': ab_norm,
            'ga_norm': ga_norm
        }
        
        print(f"  Probe {probe} Crossover: {crossover:.2f} channels")
        
        # Plot validation
        plt.figure(figsize=(6, 10))
        chans = np.arange(len(ab_norm))
        plt.plot(ab_norm, chans, 'b', label='Alpha/Beta (8-30Hz)')
        plt.plot(ga_norm, chans, 'r', label='Gamma (35-80Hz)')
        plt.axhline(crossover, color='k', linestyle='--', label=f'Crossover (ch={crossover:.1f})')
        plt.gca().invert_yaxis()
        plt.title(f"vFLIP2 Mapping: Ses {session_id} Probe {probe}")
        plt.xlabel("Normalized Power")
        plt.ylabel("Channel Number")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plot_path = os.path.join(OUTPUT_DIR, f"vflip2_ses{session_id}_probe{probe}.png")
        plt.savefig(plot_path)
        plt.close()
        
    return results

def main():
    target_sessions = {
        '230831': ['0', '1', '2'],
        '230901': ['0', '1', '2'],
        '230720': ['0', '1']
    }
    
    all_results = {}
    for sid, probes in target_sessions.items():
        all_results[sid] = process_session(sid, probes)
        
    # Save a summary report
    with open(os.path.join(OUTPUT_DIR, "vflip2_summary.txt"), "w") as f:
        f.write("vFLIP2 Spectrolaminar Mapping Summary\n")
        f.write("======================================\n\n")
        for sid, res in all_results.items():
            f.write(f"Session {sid}:\n")
            for probe, data in res.items():
                f.write(f"  Probe {probe}: Crossover at channel {data['crossover']:.2f}\n")
            f.write("\n")
            
    print(f"\nAnalysis complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
