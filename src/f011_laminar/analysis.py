# core
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def get_laminar_power(data, low, high, fs=1000):
    nyq = 0.5 * fs
    b, a = scipy.signal.butter(3, [low/nyq, high/nyq], btype='band')
    filt = scipy.signal.filtfilt(b, a, data, axis=-1)
    return np.mean(np.abs(scipy.signal.hilbert(filt, axis=-1))**2, axis=-1)

def analyze_laminar_routing(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes depth-resolved spectral power (Beta vs Gamma) during omission.
    """
    results = {}
    for area in areas:
        log.info(f"Computing Laminar for {area}")
        lfp_list = loader.get_signal(mode="lfp", condition=condition, area=area, align_to="omission")
        if not lfp_list: continue
        
        all_beta = []; all_gamma = []
        for lfp_arr in lfp_list:
            evoked = np.mean(lfp_arr, axis=0) # (channels, 2000)
            all_beta.append(get_laminar_power(evoked[:, 1000:1531], 13, 30))
            all_gamma.append(get_laminar_power(evoked[:, 1000:1531], 35, 80))
            
        def resample(profiles, n=10):
            means = []
            for p in profiles:
                means.append(np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(p)), p))
            return np.mean(means, axis=0)
            
        results[area] = {
            'depths': np.linspace(0, 1, 10),
            'beta': resample(all_beta),
            'gamma': resample(all_gamma)
        }
    return results
