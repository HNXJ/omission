# core
import numpy as np
from src.analysis.io.logger import log

def compute_waveform_metrics(waveform_mean: np.ndarray, fs: float = 30000.0):
    """
    Computes waveform duration (peak-to-trough) and half-width.
    waveform_mean: (samples,)
    Returns values in microseconds (us).
    """
    # CRITICAL FIX: Clip to a 3ms window around the trough to avoid large-buffer inflation
    # 30kHz -> 1ms = 30 samples. We take -1ms to +2ms around the trough.
    raw_trough_idx = np.argmin(waveform_mean)
    start = max(0, raw_trough_idx - 30)
    end = min(len(waveform_mean), raw_trough_idx + 60)
    
    # Work on clipped waveform
    w = waveform_mean[start:end]
    trough_idx = np.argmin(w)
    
    # 2. Peak usually follows trough in extracellular spikes
    # Find the peak after the trough
    post_trough = w[trough_idx:]
    if len(post_trough) > 1:
        peak_idx = np.argmax(post_trough) + trough_idx
        # Duration: trough to peak
        duration_us = (peak_idx - trough_idx) / fs * 1e6
    else:
        duration_us = 300.0 # Fallback
        
    # 3. Half-width: full-width at half-maximum of the trough (absolute)
    trough_val = w[trough_idx]
    half_amplitude = trough_val / 2.0
    
    # Crossings: indices where the signal crosses half-amplitude
    indices = np.where(w < half_amplitude)[0]
    if len(indices) > 0:
        half_width_us = (indices[-1] - indices[0]) / fs * 1e6
    else:
        half_width_us = 100.0
        
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
