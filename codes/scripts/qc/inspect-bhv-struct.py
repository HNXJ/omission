from codes.config.paths import BEHAVIORAL_DIR

import scipy.io as sio
import numpy as np

file_path = str(BEHAVIORAL_DIR / '230818_Cajal_glo_omission.bhv2.mat')
data = sio.loadmat(file_path)

if 'bhvUni' in data:
    bhv = data['bhvUni']
    n_trials = bhv.shape[1]
    print(f"Total trials: {n_trials}")
    
    found = False
    for i in range(min(100, n_trials)):
        trial = bhv[0, i]
        if 'AnalogData' in trial.dtype.names:
            analog = trial['AnalogData'][0, 0]
            if 'General' in analog.dtype.names:
                gen = analog['General'][0, 0]
                for gname in gen.dtype.names:
                    g_data = gen[gname][0, 0]
                    if g_data.size > 0:
                        print(f"Found non-empty data in trial {i}, field {gname}, shape {g_data.shape}")
                        print(f"First 5 samples: {g_data[:5].flatten()}")
                        found = True
                        break
        if found: break
    if not found:
        print("No non-empty General fields found in first 100 trials.")
