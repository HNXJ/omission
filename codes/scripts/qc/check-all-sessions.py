
from codes.config.paths import BEHAVIORAL_DIR

import scipy.io
import numpy as np
import os

BHV_DIR = str(BEHAVIORAL_DIR / 'omission_bhv/data')
SIDS = ['230630', '230816', '230830', '230818', '230825']

for sid in SIDS:
    try:
        f_list = [x for x in os.listdir(BHV_DIR) if sid in x and x.endswith('.mat')]
        if not f_list: continue
        f = f_list[0]
        data = scipy.io.loadmat(os.path.join(BHV_DIR, f))
        bhv = data['bhvUni'][0]
        
        counts = {}
        for t in bhv:
            if t['TrialError'][0,0] != 0: continue
            attr = str(t['TaskObject'][0,0]['Attribute'])
            id = 'A' if 'A.avi' in attr else 'B' if 'B.avi' in attr else 'Other'
            cond = 'Omit' if 'X.png' in attr else 'Std'
            key = f"{id}-{cond}"
            counts[key] = counts.get(key, 0) + 1
        print(f"Session {sid}: {counts}")
    except Exception as e:
        print(f"Error {sid}: {e}")
