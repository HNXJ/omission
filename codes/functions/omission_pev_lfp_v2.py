"""
omission_pev_lfp_v2.py: Computes PEV for LFP channels during omissions using corrected timing.
Compares AAAB vs AAAX at the p4 slot (4093-4624ms).
"""
import os
import numpy as np
import pandas as pd
import glob

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\LFP_Extractions'

# Alignment: p1 at 1000. p4 slot is at 1000 + 3*(531+500) = 1000 + 3*1031 = 4093.
# Window: 4093 to 4624 (531ms duration).
OMIT_WIN = (4000, 5000) # Slightly broader to catch onset/offset

def compute_pev(data_3d, labels):
    n_trials, n_chans, n_time = data_3d.shape
    unique_labels = np.unique(labels)
    pev_array = np.zeros((n_chans, n_time))
    
    for c in range(n_chans):
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

def process_session(session_id):
    print(f"Processing Session {session_id}...")
    # Find all probes
    probes = sorted(list(set([f.split('-')[1].replace('probe', '') for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-probe')])))
    
    results = {}
    for pid in probes:
        std_file = os.path.join(DATA_DIR, f'ses{session_id}-probe{pid}-lfp-AAAB.npy')
        omit_file = os.path.join(DATA_DIR, f'ses{session_id}-probe{pid}-lfp-AAAX.npy')
        
        if not os.path.exists(std_file) or not os.path.exists(omit_file): continue
        
        print(f"  Probe {pid}...")
        std_lfp = np.load(std_file, mmap_mode='r')
        omit_lfp = np.load(omit_file, mmap_mode='r')
        
        # Slicing around omission period
        data = np.concatenate([std_lfp[:, :, OMIT_WIN[0]:OMIT_WIN[1]], omit_lfp[:, :, OMIT_WIN[0]:OMIT_WIN[1]]], axis=0)
        labels = np.concatenate([np.zeros(len(std_lfp)), np.ones(len(omit_lfp))])
        
        results[pid] = compute_pev(data, labels)
        
    return results

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target_sessions = ['230831', '230901', '230720', '230818']
    
    all_pev = {}
    for sid in target_sessions:
        res = process_session(sid)
        for pid, pev in res.items():
            all_pev[f"{sid}_p{pid}"] = pev
            
    np.savez(os.path.join(OUTPUT_DIR, 'omission_lfp_pev_v2.npz'), **all_pev)
    print(f"PEV analysis complete. Saved to {OUTPUT_DIR}/omission_lfp_pev_v2.npz")

if __name__ == "__main__":
    main()
