# core
import numpy as np
from src.analysis.io.logger import log

def compute_waveform_metrics(waveform_mean: np.ndarray, fs: float = 30000.0):
    """
    Computes waveform duration and half-width.
    waveform_mean: (samples,)
    """
    # 1. Align to trough
    trough_idx = np.argmin(waveform_mean)
    
    # 2. Duration: trough to peak
    peak_idx = np.argmax(waveform_mean[trough_idx:]) + trough_idx
    duration = (peak_idx - trough_idx) / fs * 1000.0
    
    # 3. Half-width: time at 50% of amplitude
    # Simple thresholding
    trough_val = waveform_mean[trough_idx]
    half_max = trough_val / 2.0
    
    # Find crossings
    pre_crossing = np.where(waveform_mean[:trough_idx] > half_max)[0]
    post_crossing = np.where(waveform_mean[trough_idx:] > half_max)[0] + trough_idx
    
    half_width = 0.0
    if len(pre_crossing) > 0 and len(post_crossing) > 0:
        half_width = (post_crossing[0] - pre_crossing[-1]) / fs * 1000.0
        
    return {"duration": duration, "half_width": half_width}

def assign_putative_type(metrics: dict, threshold: float = 0.4):
    """
    Assigns E/I type based on duration.
    """
    return "Inhibitory" if metrics["duration"] < threshold else "Excitatory"
