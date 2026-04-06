
"""
vflip2_mapping.py: Improved spectro-laminar mapping based on vFLIP2 logic for ALL sessions.
Uses Alpha/Beta vs Gamma power crossover as Layer 4 marker.
Improves robustness by:
1. Dynamic session/probe discovery.
2. Robust crossover detection: finding sign change or inflection point.
3. Automatic smoothing adjustment.
4. Outputting a CSV with session, probe, and area metadata.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.ndimage import gaussian_filter1d
import glob
import re
from pynwb import NWBHDF5IO

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports\vflips'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
FS = 1000.0
BANDS = {
    'alpha_beta': (8, 30),
    'gamma': (35, 80)
}

def get_probe_area_map():
    """Maps (session, probe) -> Area using NWB metadata primarily."""
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    area_map = {}
    
    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                elec_df = nwbfile.electrodes.to_dataframe()
                
                # Default probe id mapping
                elec_df['probe_id'] = elec_df.index // 128
                probe_groups = elec_df.groupby('probe_id')

                for probe_id, group in probe_groups:
                    areas = [str(a) for a in group['location'].unique() if pd.notna(a)]
                    area_str = "/".join(areas)
                    area_map[(session_id, str(probe_id))] = area_str
        except:
            pass
            
    # Supplemental mapping from CSV if available (higher priority if specialized)
    df_path = os.path.join(CHECKPOINT_DIR, 'omission_units_identified.csv')
    if os.path.exists(df_path):
        try:
            df = pd.read_csv(df_path)
            for _, row in df.iterrows():
                sid = str(int(row['session_id']))
                pid = str(int(row['probe_id']))
                area_map[(sid, pid)] = row['area']
        except: pass
        
    return area_map

def compute_profiles(lfp_data, sigma=2.0):
    # Use samples 1000-6000 (as per previous instructions)
    # Shape: (trials, channels, time)
    # LFP data is expected to be (trials, 128, 6000)
    data = lfp_data[:, :, 1000:6000]
    n_chans = data.shape[1]
    
    profiles = {band: np.zeros(n_chans) for band in BANDS}
    for ch in range(n_chans):
        # f is frequency vector, pxx is power spectral density
        f, pxx = welch(data[:, ch, :], fs=FS, nperseg=512, axis=-1)
        mean_pxx = np.mean(pxx, axis=0) # Mean across trials
        for b, (fmin, fmax) in BANDS.items():
            profiles[b][ch] = np.mean(mean_pxx[(f >= fmin) & (f <= fmax)])
            
    # Smoothing and Normalization
    for b in profiles:
        profiles[b] = gaussian_filter1d(profiles[b], sigma=sigma)
        profiles[b] /= (np.max(profiles[b]) + 1e-12)
        
    return profiles

def find_crossover_robust(profiles):
    ab = profiles['alpha_beta']
    ga = profiles['gamma']
    diff = ga - ab
    
    # Method 1: Traditional sign change
    crossover = np.nan
    for i in range(len(diff) - 1):
        if diff[i] > 0 and diff[i+1] < 0: # Superficial (Ga > AB) -> Deep (Ga < AB)
            crossover = i + 0.5
            return crossover, "sign_change"
            
    # Method 2: Fallback to inflection point of the difference
    # If no sign change, maybe the probe is just partially superficial or deep.
    # Find the point of maximum slope in the transition.
    d_diff = np.diff(diff)
    # We want the steepest negative slope (Ga decreasing faster than AB or vice versa)
    inflection = np.argmin(d_diff) + 0.5
    
    # Only return if the slope is actually somewhat significant
    if np.abs(d_diff[int(inflection)]) > 0.01:
         return inflection, "inflection"
         
    return np.nan, "none"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    area_map = get_probe_area_map()
    summary = []
    
    # Find all AAAB LFP files
    lfp_files = glob.glob(os.path.join(DATA_DIR, '*-probe*-lfp-AAAB.npy'))
    print(f"Found {len(lfp_files)} probes to process.")

    results_list = []

    for fpath in lfp_files:
        # Parse session and probe from filename
        # Pattern: data/ses230629-probe0-lfp-AAAB.npy
        fname = os.path.basename(fpath)
        match = re.search(r'ses(\d+)-probe(\d+)', fname)
        if not match: continue
        
        sid = match.group(1)
        pid = match.group(2)
        area = area_map.get((sid, pid), "unknown")
        
        print(f"Processing {sid} P{pid} ({area})...")
        
        try:
            lfp = np.load(fpath, mmap_mode='r')
            # Increase trials to make profiles more robust
            profiles = compute_profiles(lfp, sigma=3.0) 
            crossover, method = find_crossover_robust(profiles)
            
            results_list.append({
                'session_id': sid,
                'probe_id': pid,
                'area': area,
                'crossover': crossover,
                'method': method
            })
            
            summary.append(f"Session {sid}: Probe {pid} ({area}): Crossover at {crossover:.2f} (Method: {method})")
            
            # Plot
            plt.figure(figsize=(5, 8))
            chans = np.arange(len(profiles['gamma']))
            plt.plot(profiles['alpha_beta'], chans, 'b', label='Alpha/Beta')
            plt.plot(profiles['gamma'], chans, 'r', label='Gamma')
            if not np.isnan(crossover):
                plt.axhline(crossover, color='k', ls='--', label=f'Crossover ({method})')
            plt.gca().invert_yaxis()
            plt.title(f"vFLIP2 v3: {sid} P{pid} ({area})")
            plt.legend()
            plt.savefig(os.path.join(OUTPUT_DIR, f"vflip2_{sid}_p{pid}.png"))
            plt.close()
        except Exception as e:
            print(f"  Error {sid} P{pid}: {e}")
                
    # Save Summary
    with open(os.path.join(OUTPUT_DIR, "vflip2_summary.txt"), "w") as f:
        f.write("
".join(summary))
    
    # Save CSV
    df = pd.DataFrame(results_list)
    df.to_csv(os.path.join(CHECKPOINT_DIR, "vflip2_mapping.csv"), index=False)
    
    print(f"Summary saved to {OUTPUT_DIR}/vflip2_summary.txt")
    print(f"CSV saved to {CHECKPOINT_DIR}/vflip2_mapping.csv")
    print(f"NaN count: {df['crossover'].isna().sum()}")

if __name__ == "__main__":
    main()
