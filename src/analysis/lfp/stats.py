# beta
import numpy as np
from scipy.signal import hilbert
from src.analysis.io.logger import log

def compute_modulation_index(phase_signal: np.ndarray, amplitude_signal: np.ndarray, n_bins: int = 18):
    """
    Computes the Modulation Index (Tort et al. 2010) between phase and amplitude.
    phase_signal: (N_samples,) in radians [-pi, pi]
    amplitude_signal: (N_samples,)
    """
    # 1. Bin phase into n_bins
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # 2. Average amplitude in each phase bin
    bin_indices = np.digitize(phase_signal, bins) - 1
    # Handle the boundary case (digitize returns n_bins for value == pi)
    bin_indices[bin_indices == n_bins] = n_bins - 1
    
    mean_amp = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (bin_indices == i)
        if np.any(mask):
            mean_amp[i] = np.mean(amplitude_signal[mask])
        else:
            mean_amp[i] = 0
            
    # 3. Normalize to get a probability distribution
    if np.sum(mean_amp) == 0: return 0.0
    p = mean_amp / np.sum(mean_amp)
    
    # 4. Calculate MI = (H_max - H) / H_max
    # H_max = log(n_bins)
    h_max = np.log(n_bins)
    # Shannon entropy H
    h = -np.sum(p[p > 0] * np.log(p[p > 0]))
    
    mi = (h_max - h) / h_max
    return mi

def extract_phase_amplitude(lfp: np.ndarray, fs: float, f_phase: tuple, f_amp: tuple):
    """
    Extracts phase of f_phase and amplitude envelope of f_amp using Hilbert.
    lfp: (trials, time)
    """
    from scipy.signal import butter, filtfilt
    
    # Filter for phase
    b_p, a_p = butter(4, [f_phase[0], f_phase[1]], btype='band', fs=fs)
    lfp_p = filtfilt(b_p, a_p, lfp, axis=-1)
    phase = np.angle(hilbert(lfp_p, axis=-1))
    
    # Filter for amplitude
    b_a, a_a = butter(4, [f_amp[0], f_amp[1]], btype='band', fs=fs)
    lfp_a = filtfilt(b_a, a_a, lfp, axis=-1)
    amplitude = np.abs(hilbert(lfp_a, axis=-1))
    
    return phase, amplitude
