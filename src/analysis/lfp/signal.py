# core
import numpy as np
from scipy import signal
from src.analysis.io.logger import log

def _process_lfp(data, fs=1000, nperseg=250, noverlap=245):
    """
    Trial-wise STFT for LFP TFR.
    Enforces 98% overlap (245/250) and returns linear power.
    data shape: (trials, channels, time)
    """
    log.action(f"Computing trial-wise TFR (STFT): nperseg={nperseg}, noverlap={noverlap}")
    
    # Compute TFR for the first trial/channel to get shapes
    f, t, Zxx = signal.stft(data[0, 0, :], fs=fs, nperseg=nperseg, noverlap=noverlap)
    # Zxx shape: (freqs, times)
    
    # Preallocate: (trials, channels, freqs, times)
    # Linear power = |Zxx|^2
    tfr_all = np.zeros((data.shape[0], data.shape[1], len(f), len(t)), dtype=np.float32)
    
    for tr in range(data.shape[0]):
        for ch in range(data.shape[1]):
            _, _, z = signal.stft(data[tr, ch, :], fs=fs, nperseg=nperseg, noverlap=noverlap)
            tfr_all[tr, ch, :, :] = np.abs(z)**2
            
    return f, t, tfr_all

def _process_spikes(data, sigma_ms=50):
    """
    Gaussian-smoothed PSTH.
    data shape: (trials, units, time)
    """
    log.action(f"Computing smoothed PSTH: sigma={sigma_ms}ms")
    
    # Kernel for Gaussian smoothing
    t = np.arange(-3*sigma_ms, 3*sigma_ms + 1)
    kernel = np.exp(-t**2 / (2 * sigma_ms**2))
    kernel /= kernel.sum()
    
    psth_all = np.mean(data, axis=0) # (units, time)
    smoothed = np.zeros_like(psth_all)
    for u in range(psth_all.shape[0]):
        smoothed[u, :] = np.convolve(psth_all[u, :], kernel, mode='same')
        
    return smoothed
