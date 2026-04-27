import numpy as np
from scipy import signal
from src.analysis.lfp.lfp_constants import FS_LFP

def preprocess_lfp(lfp: np.ndarray, fs: float = FS_LFP) -> np.ndarray:
    """
    Canonical preprocessing:
    1. Highpass filter (1Hz) to remove slow drifts.
    2. Common Average Referencing (CAR) across channels.
    lfp shape: (trials, channels, time)
    """
    # 1. Highpass 1Hz
    b, a = signal.butter(4, 1.0 / (0.5 * fs), btype='high')
    lfp_filt = signal.filtfilt(b, a, lfp, axis=-1)
    
    # 2. CAR
    # subtract mean across channels for each trial and timepoint
    car = np.mean(lfp_filt, axis=1, keepdims=True)
    lfp_preproc = lfp_filt - car
    
    return lfp_preproc

def baseline_normalize(power: np.ndarray, times: np.ndarray, baseline_window: tuple = (-250, -50)) -> np.ndarray:
    """
    Baseline normalization in dB: 10*log10(P / baseline).
    Ensures no -inf or NaN values via np.maximum and nan_to_num.
    """
    mask = (times >= baseline_window[0]) & (times <= baseline_window[1])
    baseline = np.mean(power[..., mask], axis=-1, keepdims=True)
    
    # Floor at 1e-12 to prevent log10(0) -> -inf
    safe_power = np.maximum(power, 1e-12)
    safe_baseline = np.maximum(baseline, 1e-12)
    
    normed = 10.0 * np.log10(safe_power / safe_baseline)
    
    # Final cleanup of any mathematical artifacts
    return np.nan_to_num(normed, nan=0.0, posinf=0.0, neginf=0.0)
