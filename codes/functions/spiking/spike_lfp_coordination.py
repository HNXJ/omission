
import numpy as np
import scipy.signal as signal
from scipy.fftpack import hilbert

def compute_ppc(phases):
    """
    Computes Pairwise Phase Consistency (PPC) - Vinck et al. 2010.
    Input: phases (N,) - array of phases in radians
    Output: ppc score (scalar)
    """
    n = len(phases)
    if n < 2:
        return np.nan
        
    # Vectorized PPC computation:
    # PPC = (|sum(exp(i*theta))|^2 - N) / (N*(N-1))
    sum_exp = np.sum(np.exp(1j * phases))
    abs_sum_sq = np.abs(sum_exp)**2
    ppc = (abs_sum_sq - n) / (n * (n - 1))
    
    return ppc

def get_band_phase(lfp, band, fs=1000):
    """
    Filters LFP in a band and returns the instantaneous phase.
    Input: lfp (Trials, Time)
    Output: phase (Trials, Time)
    """
    low, high = band
    nyq = 0.5 * fs
    b, a = signal.butter(4, [low / nyq, high / nyq], btype='band')
    
    # Zero-phase filtering
    filtered = signal.filtfilt(b, a, lfp, axis=-1)
    
    # Hilbert transform to get phase
    # scipy.signal.hilbert is more robust than scipy.fftpack.hilbert for this
    analytic = signal.hilbert(filtered, axis=-1)
    phase = np.angle(analytic)
    
    return phase

def compute_spike_lfp_ppc_trace(spikes, lfp_phase, win_size=200, step=50):
    """
    Computes time-resolved PPC between spikes and LFP phase.
    Input: 
        spikes (Trials, Time) - binary array
        lfp_phase (Trials, Time) - phase array
    Output:
        ppc_trace (TimeBins,)
    """
    n_trials, n_time = spikes.shape
    time_bins = np.arange(0, n_time - win_size + 1, step)
    ppc_trace = np.zeros(len(time_bins))
    
    for i, t in enumerate(time_bins):
        # Extract spikes and corresponding phases in the window
        win_spikes = spikes[:, t:t+win_size]
        win_phases = lfp_phase[:, t:t+win_size]
        
        # Flatten and get phases where spikes occur
        spike_indices = np.where(win_spikes > 0)
        phases_at_spikes = win_phases[spike_indices]
        
        if len(phases_at_spikes) > 10:
            ppc_trace[i] = compute_ppc(phases_at_spikes)
        else:
            ppc_trace[i] = np.nan
            
    return ppc_trace, time_bins

def compute_spike_lfp_power_corr(spikes, lfp_power, win_size=200, step=50):
    """
    Computes correlation between firing rate and LFP power in a window across trials.
    Input:
        spikes (Trials, Time)
        lfp_power (Trials, Time)
    """
    n_trials, n_time = spikes.shape
    time_bins = np.arange(0, n_time - win_size + 1, step)
    corr_trace = np.zeros(len(time_bins))
    
    for i, t in enumerate(time_bins):
        # Average FR and Power across window for each trial
        fr_per_trial = np.mean(spikes[:, t:t+win_size], axis=1)
        pow_per_trial = np.mean(lfp_power[:, t:t+win_size], axis=1)
        
        if np.std(fr_per_trial) > 0 and np.std(pow_per_trial) > 0:
            corr_trace[i] = np.corrcoef(fr_per_trial, pow_per_trial)[0, 1]
        else:
            corr_trace[i] = np.nan
            
    return corr_trace, time_bins
