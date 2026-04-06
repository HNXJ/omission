
from codes.config.paths import BEHAVIORAL_DIR

import scipy.io
import numpy as np

MAT_FILE = str(BEHAVIORAL_DIR / 'omission_bhv/data/230830_Cajal_glo_omission.bhv2.mat')
data = scipy.io.loadmat(MAT_FILE)
bhv = data['bhvUni'][0]

counts = {}
for i in range(len(bhv)):
    t = bhv[i]
    if t['TrialError'][0,0] != 0:
        continue
    
    attr = str(t['TaskObject'][0,0]['Attribute'])
    
    # Precise Identity check
    if 'A.avi' in attr: id = 'A'
    elif 'B.avi' in attr: id = 'B'
    else: id = 'Other'
    
    # Precise Omission check
    if 'X.png' in attr: cond = 'Omit'
    else: cond = 'Std'
    
    key = f"{id}-{cond}"
    counts[key] = counts.get(key, 0) + 1

print("Trial counts in session 230830:")
for k, v in counts.items():
    print(f"  {k}: {v}")
