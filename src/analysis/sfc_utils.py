# core
import numpy as np
import scipy.signal
from src.core.logger import log

def calculate_plv(lfp, spikes, fs=1000, freq_band=(13, 30), subsample_spikes=True):
    """
    Computes Phase-Locking Value (PLV) for a specific frequency band.
    lfp: (trials, time) or (time,)
    spikes: (trials, time) or (time,) - Binary array (1 at spike time, 0 otherwise)
    subsample_spikes: If True, equates spike count across comparisons (handled at higher level).
    """
    # 1. Bandpass filter the LFP
    nyq = 0.5 * fs
    low, high = freq_band[0] / nyq, freq_band[1] / nyq
    b, a = scipy.signal.butter(4, [low, high], btype='bandpass')
    
    # Apply filter along time axis
    filtered_lfp = scipy.signal.filtfilt(b, a, lfp, axis=-1)
    
    # 2. Extract Phase via Hilbert Transform
    analytic_signal = scipy.signal.hilbert(filtered_lfp, axis=-1)
    phase_lfp = np.angle(analytic_signal)
    
    # 3. Identify Phases at Spike Times
    spike_indices = np.where(spikes > 0)
    # spike_indices is tuple: (trial_indices, time_indices) if 2D, else (time_indices,)
    spike_phases = phase_lfp[spike_indices]
    
    if len(spike_phases) == 0:
        return 0.0, np.array([])
        
    # 4. Compute Mean Resultant Vector (PLV)
    # PLV = |1/N * sum(exp(i * theta))|
    complex_phases = np.exp(1j * spike_phases)
    plv = np.abs(np.mean(complex_phases))
    
    return plv, spike_phases

def get_plv_spectrum(lfp, spikes, fs=1000, n_bins=30):
    """
    Sweep through frequencies to see the full SFC (PLV) spectrum.
    """
    freqs = np.logspace(np.log10(2), np.log10(100), n_bins)
    plv_vals = []
    
    for f in freqs:
        bw = max(2.0, f * 0.2)
        low = f - bw/2
        high = f + bw/2
        if high >= 500: high = 499 # Nyquist guard
        if low <= 0: low = 0.1
        
        plv, _ = calculate_plv(lfp, spikes, fs, freq_band=(low, high))
        plv_vals.append(plv)
        
    return freqs, np.array(plv_vals)

def apply_subsampling(spikes_list, target_count=None):
    """
    Subsamples spikes to match a target count to avoid firing-rate bias in PLV.
    spikes_list: List of binary spike arrays.
    """
    counts = [np.sum(s > 0) for s in spikes_list]
    if target_count is None:
        target_count = min(counts)
        
    log.info(f"[action] Subsampling spikes to target count: {target_count}")
    
    new_spikes = []
    for s in spikes_list:
        idx = np.where(s > 0)
        total = len(idx[0])
        if total > target_count:
            keep = np.random.choice(total, target_count, replace=False)
            # Create fresh binary mask
            s_new = np.zeros_like(s)
            # Multi-dim indexing
            if len(idx) == 2:
                s_new[idx[0][keep], idx[1][keep]] = 1
            else:
                s_new[idx[0][keep]] = 1
            new_spikes.append(s_new)
        else:
            new_spikes.append(s)
    return new_spikes
