import numpy as np
import pandas as pd
import h5py
import os
import re
import glob
from pathlib import Path
from scipy.stats import ttest_ind, pearsonr
from scipy.signal import hilbert

# Constants
FS_LFP = 1000
BIN_MS = 50

# Windows (Samples relative to Code 101.0 at 1000)
WINDOWS = {
    'fx': (500, 1000),
    'p1': (1000, 1531), 'd1': (1531, 2031),
    'p2': (2031, 2562), 'd2': (2562, 3062),
    'p3': (3062, 3593), 'd3': (3593, 4093),
    'p4': (4093, 4624), 'd4': (4624, 5124)
}

def get_lfp_envelope(data):
    """Calculates LFP envelope using Hilbert transform."""
    # data: (Trials, Time)
    analytical_signal = hilbert(data, axis=1)
    amplitude_envelope = np.abs(analytical_signal)
    return amplitude_envelope

def classify_lfp_refined():
    data_dir = Path(__file__).parents[2] / "data"
    checkpoint_dir = Path(__file__).parents[2] / "output" / "checkpoints"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    files = glob.glob(f'{data_dir}/lfp_by_area_ses-*.h5')
    all_lfp_channels = []
    
    for f_path in files:
        ses = re.search(r'ses-(\d+)', f_path).group(1)
        print(f"Classifying LFP channels for Session {ses}...")
        
        # Load eye data for correlation
        eye_f = glob.glob(f'{data_dir}/ses{ses}-behavioral-AAAB.npy')
        eye_vel = None
        if eye_f:
            eye_data = np.load(eye_f[0], mmap_mode='r')
            ex, ey = eye_data[:, 0, :], eye_data[:, 1, :]
            vx, vy = np.gradient(ex, axis=1), np.gradient(ey, axis=1)
            eye_vel = np.sqrt(vx**2 + vy**2) # (Trials, Time)

        with h5py.File(f_path, 'r') as f:
            for area_key in f.keys():
                # area_key might be "V1,V2"
                data = f[area_key][:] # (Trials, Channels, Time)
                n_trials, n_chans, n_time = data.shape
                
                # Check condition counts
                # This H5 format usually pools trials? 
                # Need to verify if the H5 has condition labels.
                # If not, I might need to load the raw .npy files.
                # Wait, the H5 files I created earlier were by area, but they didn't have condition labels.
                # I should probably use the .npy files directly for classification to distinguish AAAB/BBBA.
                pass

    print("Note: H5 files lack condition labels. Switching to .npy discovery for LFP classification.")

def classify_lfp_from_npy():
    data_dir = Path(__file__).parents[2] / "data"
    checkpoint_dir = Path(__file__).parents[2] / "output" / "checkpoints"
    
    sessions = sorted(list(set([re.search(r'ses(\d+)', f).group(1) for f in glob.glob(f'{data_dir}/ses*-probe*-lfp-*.npy')])))
    
    all_lfp_meta = []
    
    for ses in sessions:
        print(f"Processing Session {ses} (LFP)...")
        conds = ['AAAB', 'BBBA', 'AXAB', 'BXBA']
        
        # Discover probes
        probes = sorted(list(set([int(re.search(r'probe(\d+)', f).group(1)) for f in glob.glob(f'{data_dir}/ses{ses}-probe*-lfp-AAAB.npy')])))
        
        # Load eye data
        eye_f = glob.glob(f'{data_dir}/ses{ses}-behavioral-AAAB.npy')
        eye_vel_p1 = None
        if eye_f:
            eye_data = np.load(eye_f[0], mmap_mode='r')
            ex, ey = eye_data[:, 0, 1000:1531], eye_data[:, 1, 1000:1531]
            eye_vel_p1 = np.mean(np.sqrt(np.gradient(ex, axis=1)**2 + np.gradient(ey, axis=1)**2), axis=1)

        for p in probes:
            # Load LFP for AAAB
            f_aaab = f'{data_dir}/ses{ses}-probe{p}-lfp-AAAB.npy'
            f_bbba = f'{data_dir}/ses{ses}-probe{p}-lfp-BBBA.npy'
            f_axab = f'{data_dir}/ses{ses}-probe{p}-lfp-AXAB.npy'
            
            if not os.path.exists(f_aaab): continue
            
            data_a = np.load(f_aaab, mmap_mode='r') # (Trials, Chans, Time)
            n_chans = data_a.shape[1]
            
            data_b = np.load(f_bbba, mmap_mode='r') if os.path.exists(f_bbba) else None
            data_ax = np.load(f_axab, mmap_mode='r') if os.path.exists(f_axab) else None
            
            for ch in range(n_chans):
                # Use LFP Envelope for magnitude-based classification
                env_a = get_lfp_envelope(data_a[:, ch, :])
                
                resp_a = np.mean(env_a[:, 1000:1531], axis=1) # P1 Magnitude
                base = np.mean(env_a[:, 500:1000], axis=1) # FX Magnitude
                
                # Stim Selectivity
                is_selective = False
                is_agnostic = False
                if data_b is not None:
                    env_b = get_lfp_envelope(data_b[:, ch, :])
                    resp_b = np.mean(env_b[:, 1000:1531], axis=1)
                    _, p_val = ttest_ind(resp_a, resp_b)
                    is_stim = (np.mean(resp_a) > np.mean(base)*1.1) or (np.mean(resp_b) > np.mean(base)*1.1)
                    is_selective = p_val < 0.05 and is_stim
                    is_agnostic = p_val >= 0.05 and is_stim
                
                # Omission Preference
                is_omit = False
                if data_ax is not None:
                    env_ax = get_lfp_envelope(data_ax[:, ch, :])
                    resp_omit = np.mean(env_ax[:, 2031:2562], axis=1) # P2 Omission
                    resp_normal = np.mean(env_a[:, 2031:2562], axis=1) # P2 Normal
                    _, p_val_omit = ttest_ind(resp_omit, resp_normal)
                    is_omit = p_val_omit < 0.05 and np.mean(resp_omit) > np.mean(resp_normal)
                
                # Eye Correlation
                is_eye = False
                if eye_vel_p1 is not None and len(resp_a) == len(eye_vel_p1):
                    _, p_val_eye = pearsonr(resp_a, eye_vel_p1)
                    is_eye = p_val_eye < 0.05
                
                categories = []
                if is_selective: categories.append('Stim-Selective')
                if is_agnostic: categories.append('Stim-Agnostic')
                if is_omit: categories.append('Omit-Pref')
                if is_eye: categories.append('Eye-Corr')
                if not categories: categories.append('Other')
                
                all_lfp_meta.append({
                    'session': ses, 'probe': p, 'channel': ch,
                    'is_selective': is_selective, 'is_agnostic': is_agnostic,
                    'is_omit': is_omit, 'is_eye': is_eye,
                    'category': '|'.join(categories)
                })
                
    df = pd.DataFrame(all_lfp_meta)
    df.to_csv(f'{checkpoint_dir}/enhanced_lfp_categories.csv', index=False)
    print(f"LFP classification complete. Count: {len(df)}")


def main(args=None):
    classify_lfp_from_npy()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
