# beta
import numpy as np
from scipy.signal import welch
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_spectral_fingerprints(loader: DataLoader, sessions: list, areas: list, condition="AXAB"):
    """
    Extracts the PSD for each area during the omission window.
    """
    results = {area: [] for area in areas}
    freqs = None
    
    for ses in sessions:
        log.info(f"Analyzing Spectral Fingerprints for Session: {ses}")
        for area in areas:
            lfp_matches = loader.get_signal(mode="lfp", condition=condition, area=area, session=ses)
            if not lfp_matches: continue
            
            lfp = lfp_matches[0] # (trials, channels, time)
            # Omission window: 1031 to 1562
            lfp_omit = lfp[:, :, 1031:1562]
            
            # Compute PSD for each channel/trial and average
            # Flatten trials and channels
            data_flat = lfp_omit.reshape(-1, lfp_omit.shape[-1])
            f, pxx = welch(data_flat, fs=1000.0, nperseg=256)
            
            if freqs is None: freqs = f
            
            results[area].append(np.mean(pxx, axis=0))
            
    # Average across sessions
    final_results = {}
    for area in areas:
        if results[area]:
            final_results[area] = np.mean(results[area], axis=0)
            
    return freqs, final_results
