# core
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.lfp_pipeline import get_lfp_signal
from src.analysis.lfp.lfp_preproc import preprocess_lfp

def get_band_power(data, lowcut, highcut, fs):
    nyq = 0.5 * fs
    b, a = scipy.signal.butter(4, [lowcut/nyq, highcut/nyq], btype='band')
    filtered = scipy.signal.filtfilt(b, a, data)
    env = np.abs(scipy.signal.hilbert(filtered))
    return env ** 2

def analyze_spectral_harmony(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes cross-area envelope correlation matrices for Beta and Gamma bands.
    """
    n = len(areas)
    beta_omit = np.zeros((n, 2000))
    gamma_omit = np.zeros((n, 2000))
    
    for i, area in enumerate(areas):
        lfp = get_lfp_signal(area, condition, align_to="omission")
        if lfp.size == 0: continue
        lfp_clean = preprocess_lfp(lfp)
        evoked = np.mean(lfp_clean, axis=(0, 1))
        
        beta_omit[i, :] = get_band_power(evoked, 13, 30, 1000)
        gamma_omit[i, :] = get_band_power(evoked, 35, 80, 1000)
        
    def corr_mat(data, win):
        m = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                si, sj = data[i, win[0]:win[1]], data[j, win[0]:win[1]]
                if np.std(si) > 1e-10 and np.std(sj) > 1e-10:
                    m[i, j] = np.corrcoef(si, sj)[0, 1]
        return m
        
    results = {
        "Beta_Baseline": corr_mat(beta_omit, (750, 950)),
        "Beta_Omission": corr_mat(beta_omit, (1000, 1531)),
        "Gamma_Baseline": corr_mat(gamma_omit, (750, 950)),
        "Gamma_Omission": corr_mat(gamma_omit, (1000, 1531))
    }
    return results
