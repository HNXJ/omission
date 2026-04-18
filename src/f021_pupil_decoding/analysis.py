# beta
import numpy as np
import os
from src.analysis.io.logger import log

def analyze_pupil_surprise(sessions: list, condition_omit="AXAB", condition_std="AAAB"):
    """
    Analyzes pupil diameter changes during omissions vs standard stimuli.
    Returns: {session: { 'omit': (time,), 'std': (time,) }}
    """
    results = {}
    data_dir = "D:/drive/data/behavioral"
    
    for ses in sessions:
        log.info(f"Analyzing Pupil Surprise for Session: {ses}")
        
        path_omit = os.path.join(data_dir, f"ses{ses}-behavioral-{condition_omit}.npy")
        path_std = os.path.join(data_dir, f"ses{ses}-behavioral-{condition_std}.npy")
        
        if not os.path.exists(path_omit) or not os.path.exists(path_std):
            log.warning(f"Missing behavioral data for {ses}")
            continue
            
        # Channel 2 is Pupil
        bhv_omit = np.load(path_omit, mmap_mode='r')
        bhv_std = np.load(path_std, mmap_mode='r')
        
        # Mean across trials for Pupil channel (idx 2)
        pupil_omit = np.nanmean(bhv_omit[:, 2, :], axis=0)
        pupil_std = np.nanmean(bhv_std[:, 2, :], axis=0)
        
        # Baseline normalize (to fixation window 500-1000ms relative to array start)
        # Assuming sample 1000 is P1 onset
        base_omit = np.mean(pupil_omit[500:1000])
        base_std = np.mean(pupil_std[500:1000])
        
        results[ses] = {
            'omit': pupil_omit - base_omit,
            'std': pupil_std - base_std
        }
        
    return results
