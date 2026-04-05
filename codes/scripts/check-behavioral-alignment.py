
import numpy as np
import scipy.io
import os
from pathlib import Path

MAT_FILE = Path(__file__).parents[2] / "data" / "behavioral" / "omission_bhv" / "data" / "230830_Cajal_glo_omission.bhv2.mat"
NPY_FILE = Path(__file__).parents[2] / "data" / "ses230830-behavioral-AAAB.npy"

# 1. Load MAT
data_mat = scipy.io.loadmat(MAT_FILE)
bhv = data_mat['bhvUni'][0]

# Find trials with condition 1 (AAAB)
trials_aaab_mat = []
for i in range(len(bhv)):
    if bhv[i]['Condition'][0,0] == 1 and bhv[i]['TrialError'][0,0] == 0:
        trials_aaab_mat.append(bhv[i]['AnalogData']['Eye'][0,0])

# 2. Load NPY
data_npy = np.load(NPY_FILE)

print(f"MAT AAAB trials: {len(trials_aaab_mat)}, NPY trials: {len(data_npy)}")

# Compare trial 0
mat_eye = trials_aaab_mat[0]
npy_eye = data_npy[0]

# Correlations
for ch in range(4):
    # NPY is 6000 points. MAT is N points.
    # Need to find the start of the trial in MAT or align.
    # Actually, if they are already aligned, just interpolate or crop.
    n = min(len(mat_eye), len(npy_eye[ch]))
    corr_x = np.corrcoef(mat_eye[:n, 0], npy_eye[ch, :n])[0,1]
    corr_y = np.corrcoef(mat_eye[:n, 1], npy_eye[ch, :n])[0,1]
    print(f"Ch {ch} Corr with MAT-X: {corr_x:.3f}, MAT-Y: {corr_y:.3f}")

# Check means again
print(f"NPY Means: {np.mean(data_npy, axis=(0, 2))}")
