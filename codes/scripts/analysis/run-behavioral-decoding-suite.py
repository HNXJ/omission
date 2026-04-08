from codes.config.paths import DATA_DIR, FIGURES_DIR

import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from scipy.signal import savgol_filter

# Global Aesthetics
plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#000000'
plt.rcParams['figure.facecolor'] = '#000000'
plt.rcParams['axes.edgecolor'] = '#708090'
plt.rcParams['text.color'] = '#FFFFFF'
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
SLATE = '#708090'

def detect_saccades_nwb(eye_x, eye_y, fs=1000, thresh=3.5):
    """Detects eye-movement events based on Z-scored velocity."""
    vx = np.gradient(eye_x) * fs
    vy = np.gradient(eye_y) * fs
    vel = np.sqrt(vx**2 + vy**2)
    # Z-score velocity to find outliers (saccades)
    z_vel = (vel - np.mean(vel)) / np.std(vel)
    indices = np.where(z_vel > thresh)[0]
    return indices, vel

def get_polar_direction(eye_x, eye_y):
    """Calculates the polar direction of eye-movements."""
    dx = np.diff(eye_x)
    dy = np.diff(eye_y)
    angles = np.arctan2(dy, dx)
    return np.degrees(angles) % 360

def analyze_session_eye(data_dir, session_id):
    """Analyzes eye signals for a specific session across conditions."""
    files = [f for f in os.listdir(data_dir) if f.startswith(f'ses{session_id}-behavioral') and f.endswith('.npy')]
    results = {}
    for f in files:
        cond_name = f.split('-')[-1].replace('.npy', '')
        data = np.load(os.path.join(data_dir, f)) # (N_trials, 4, 6000)
        # Channel mapping: 0:X, 1:Y, 2:Pupil, 3:PD
        eye_x = data[:, 0, :]
        eye_y = data[:, 1, :]
        pupil = data[:, 2, :]
        # Basic Z-score normalization for alignment across trials
        eye_x = (eye_x - np.mean(eye_x)) / np.std(eye_x)
        eye_y = (eye_y - np.mean(eye_y)) / np.std(eye_y)
        pupil = (pupil - np.mean(pupil)) / np.std(pupil)
        results[cond_name] = {
            'eye_x': eye_x,
            'eye_y': eye_y,
            'pupil': pupil
        }
    return results

def decode_identity_eye(session_results):
    """Decodes Stimulus Identity (AAAB vs BBBA) from eye-signals."""
    if 'AAAB' not in session_results or 'BBBA' not in session_results:
        return None
    aaab = session_results['AAAB']
    bbba = session_results['BBBA']
    # Feature engineering: Mean EyeX, EyeY, Pupil in 100ms bins
    n_trials_a = aaab['eye_x'].shape[0]
    n_trials_b = bbba['eye_x'].shape[0]
    n_samples = aaab['eye_x'].shape[1]
    bin_size = 100
    n_bins = n_samples // bin_size
    X = []
    y = []
    # Class A (AAAB)
    for i in range(n_trials_a):
        features = []
        for b in range(n_bins):
            start, end = b*bin_size, (b+1)*bin_size
            features.append(np.mean(aaab['eye_x'][i, start:end]))
            features.append(np.mean(aaab['eye_y'][i, start:end]))
            features.append(np.mean(aaab['pupil'][i, start:end]))
        X.append(features)
        y.append(0)
    # Class B (BBBA)
    for i in range(n_trials_b):
        features = []
        for b in range(n_bins):
            start, end = b*bin_size, (b+1)*bin_size
            features.append(np.mean(bbba['eye_x'][i, start:end]))
            features.append(np.mean(bbba['eye_y'][i, start:end]))
            features.append(np.mean(bbba['pupil'][i, start:end]))
        X.append(features)
        y.append(1)
    X = np.array(X)
    y = np.array(y)
    # Time-resolved decoding
    skf = StratifiedKFold(n_splits=5, shuffle=True)
    bin_scores = []
    for b in range(n_bins):
        # Extract features for this bin only
        X_bin = X[:, b*3:(b+1)*3] # EyeX, EyeY, Pupil for this bin
        scores = []
        for train_idx, test_idx in skf.split(X_bin, y):
            model = SVC(kernel='linear')
            model.fit(X_bin[train_idx], y[train_idx])
            scores.append(model.score(X_bin[test_idx], y[test_idx]))
        bin_scores.append(np.mean(scores))
    return np.array(bin_scores)

def main(args=None):
    data_dir = DATA_DIR
    session_id = "230629"
    results = analyze_session_eye(data_dir, session_id)
    identity_scores = decode_identity_eye(results)
    if identity_scores is not None:
        plt.figure(figsize=(10, 4))
        time_bins = np.arange(len(identity_scores)) * 100 - 1000 # -1000 to 5000
        plt.plot(time_bins, identity_scores, color=GOLD, linewidth=2, label='Identity A vs B')
        plt.axhline(0.5, color=SLATE, linestyle='--', label='Chance')
        plt.axvline(0, color='#FFFFFF', alpha=0.5, label='P1 Onset')
        plt.title(f'Behavioral Identity Decoding: Session {session_id}', color=GOLD)
        plt.xlabel('Time (ms)', color=SLATE)
        plt.ylabel('Decoding Accuracy', color=SLATE)
        plt.legend()
        plt.tight_layout()
        fig_path = os.path.join(FIGURES_DIR, f"FIG_Eye_Identity_Decoding_{session_id}.png")
        plt.savefig(fig_path, dpi=300)
        print(f"Saved identity decoding plot to {fig_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
