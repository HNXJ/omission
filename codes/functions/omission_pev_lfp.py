"""
omission_pev_lfp.py: Computes PEV (Percentage of Explained Variance) for LFP channels during omissions.
Tests for depth-specific omission signals across brain areas.
"""
import os
import numpy as np
import pandas as pd
import h5py
from scipy.stats import f_oneway

LFP_H5_DIR = r'D:\Analysis\Omission\local-workspace'
VFLIP_SUMMARY_PATH = r'D:\Analysis\Omission\local-workspace\LFP_Extractions\vflip2_summary.txt'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\LFP_Extractions'

def compute_pev(data_3d, labels):
    """
    Computes PEV for each channel and timepoint.
    data_3d: (Trials, Channels, Time)
    labels: (Trials,) - condition IDs
    """
    n_trials, n_chans, n_time = data_3d.shape
    unique_labels = np.unique(labels)
    pev_array = np.zeros((n_chans, n_time))
    
    for c in range(n_chans):
        # We'll compute PEV at each timepoint
        for t in range(n_time):
            y = data_3d[:, c, t]
            var_total = np.var(y)
            if var_total <= 1e-10: continue
            
            ss_error = 0
            for label in unique_labels:
                group = y[labels == label]
                if len(group) > 0:
                    ss_error += np.sum((group - np.mean(group))**2)
            
            var_error = ss_error / n_trials
            pev_array[c, t] = (var_total - var_error) / (var_total + 1e-10)
            
    return pev_array

def process_lfp_pev(session_id):
    h5_path = os.path.join(LFP_H5_DIR, f'lfp_by_area_ses-{session_id}.h5')
    if not os.path.exists(h5_path): return
    
    print(f"Analyzing PEV for Session {session_id}...")
    with h5py.File(h5_path, 'r') as f:
        areas = list(f.keys())
        results = {}
        
        for area in areas:
            print(f"  Area: {area}")
            # Combine 'AAAB' (Standard) vs 'AAAX' (Omission) for PEV
            # Or use multiple omission variants
            std_data = f[area]['AAAB'][:] # (Trials, Chans, Samples)
            omit_data = f[area]['AAAX'][:]
            
            # Combine data
            combined_data = np.concatenate([std_data, omit_data], axis=0)
            labels = np.concatenate([np.zeros(len(std_data)), np.ones(len(omit_data))])
            
            # Focus on 4000-5000ms window (omission)
            # Downsample to save time if needed, but let's try raw 1kHz for now
            pev = compute_pev(combined_data[:, :, 4000:5000], labels)
            results[area] = pev
            
    return results

def main():
    target_sessions = ['230831', '230901', '230720']
    all_pev = {}
    for sid in target_sessions:
        all_pev[sid] = process_lfp_pev(sid)
        
    # Save results as .npz for later plotting
    np.savez(os.path.join(OUTPUT_DIR, 'omission_lfp_pev.npz'), **{f"{sid}_{area}": all_pev[sid][area] for sid in all_pev for area in all_pev[sid]})
    print(f"\nPEV analysis complete. Saved to {OUTPUT_DIR}/omission_lfp_pev.npz")

if __name__ == "__main__":
    main()
