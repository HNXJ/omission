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
    Uses trial-wise correlations to preserve structure.
    """
    n = len(areas)
    # Collect trial-wise power envelopes for all areas
    # Dict: area -> {band: (trials, time)}
    envelopes = {area: {} for area in areas}
    
    for area in areas:
        lfp = get_lfp_signal(area, condition, align_to="omission")
        if lfp.size == 0: continue
        lfp_clean = preprocess_lfp(lfp)
        
        # Average across channels first
        area_lfp = np.mean(lfp_clean, axis=1) # (trials, time)
        
        for band_name, (low, high) in [("Beta", (13, 30)), ("Gamma", (35, 80))]:
            nyq = 0.5 * 1000.0
            b, a = scipy.signal.butter(4, [low/nyq, high/nyq], btype='band')
            filt = scipy.signal.filtfilt(b, a, area_lfp, axis=-1)
            env = np.abs(scipy.signal.hilbert(filt, axis=-1))**2
            envelopes[area][band_name] = env
            
    def compute_harmony(band, win):
        mat = np.zeros((n, n))
        for i, a1 in enumerate(areas):
            for j, a2 in enumerate(areas):
                if band in envelopes[a1] and band in envelopes[a2]:
                    e1 = envelopes[a1][band][:, win[0]:win[1]]
                    e2 = envelopes[a2][band][:, win[0]:win[1]]
                    # Compute mean trial-wise correlation
                    corrs = []
                    for t in range(e1.shape[0]):
                        if np.std(e1[t]) > 1e-10 and np.std(e2[t]) > 1e-10:
                            corrs.append(np.corrcoef(e1[t], e2[t])[0, 1])
                    if corrs:
                        mat[i, j] = np.mean(corrs)
        return mat
        
    results = {
        "Beta_Baseline": compute_harmony("Beta", (750, 950)),
        "Beta_Omission": compute_harmony("Beta", (1000, 1531)),
        "Gamma_Baseline": compute_harmony("Gamma", (750, 950)),
        "Gamma_Omission": compute_harmony("Gamma", (1000, 1531))
    }
    return results
