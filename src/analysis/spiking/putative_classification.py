# core
import numpy as np
from src.analysis.io.logger import log

def compute_waveform_metrics(waveform_mean: np.ndarray, fs: float = 30000.0):
    """
    Computes waveform duration and half-width.
    waveform_mean: (samples,)
    Returns values in microseconds (us).
    """
    # 1. Align to trough
    trough_idx = np.argmin(waveform_mean)
    
    # 2. Duration: trough to peak (in microseconds)
    # Ensure peak exists after trough
    if trough_idx < len(waveform_mean) - 1:
        peak_idx = np.argmax(waveform_mean[trough_idx:]) + trough_idx
        duration_us = (peak_idx - trough_idx) / fs * 1e6
    else:
        duration_us = 0.0
        
    # 3. Bound physically impossible values (Max 2000us / 2ms)
    duration_us = min(duration_us, 2000.0)
    
    # 4. Half-width: time at 50% of amplitude
    trough_val = waveform_mean[trough_idx]
    half_max = trough_val / 2.0
    
    # Find crossings
    pre_crossing = np.where(waveform_mean[:trough_idx] > half_max)[0]
    post_crossing = np.where(waveform_mean[trough_idx:] > half_max)[0] + trough_idx
    
    half_width_us = 0.0
    if len(pre_crossing) > 0 and len(post_crossing) > 0:
        half_width_us = (post_crossing[0] - pre_crossing[-1]) / fs * 1e6
    
    # Bound half-width
    half_width_us = min(half_width_us, 2000.0)
        
    return {"duration_us": duration_us, "half_width_us": half_width_us}

def is_stable_plus(unit_metrics: dict, spk_train: np.ndarray, min_fr: float = 1.0, min_pr: float = 0.98, min_snr: float = 0.5):
    """
    Checks if a unit qualifies as 'Stable-Plus'.
    spk_train: (trials, time)
    """
    # Firing rate
    total_spikes = np.sum(spk_train)
    duration_s = spk_train.shape[0] * spk_train.shape[1] / 1000.0
    fr = total_spikes / duration_s
    
    # Presence ratio (fraction of time bins with at least one spike)
    # This is a proxy; presence_ratio should ideally be provided in unit_metrics if precomputed
    # For now, approximate by trial-wise presence
    trial_sums = np.sum(spk_train, axis=1)
    pr = np.mean(trial_sums > 0)
    
    # SNR (Placeholder: assuming provided in unit_metrics)
    snr = unit_metrics.get("snr", 0.0)
    
    # Consistency: non-zero firing rate on every single trial
    all_trials_active = np.all(trial_sums > 0)
    
    return (fr >= min_fr) and (pr >= min_pr) and (snr >= min_snr) and all_trials_active

def assign_putative_type(metrics: dict, threshold_us: float = 400.0):
    """
    Assigns E/I type based on duration (threshold in microseconds).
    E: > 400us, I: < 400us.
    """
    return "Inhibitory" if metrics["duration_us"] < threshold_us else "Excitatory"
