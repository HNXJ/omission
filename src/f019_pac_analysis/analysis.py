# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.stats import extract_phase_amplitude, compute_modulation_index

def analyze_pac(loader: DataLoader, sessions: list, areas: list, condition="AXAB"):
    """
    Computes PAC (Modulation Index) for specific phase and amplitude bands.
    Phase: Beta (13-30 Hz), Amplitude: Gamma (35-80 Hz).
    Returns: {area: [mi_values]}
    """
    results = {area: [] for area in areas}
    
    f_phase = (13, 30) # Beta
    f_amp = (35, 80)   # Gamma
    
    for ses in sessions:
        log.info(f"Analyzing PAC for Session: {ses}")
        for area in areas:
            lfp_matches = loader.get_signal(mode="lfp", condition=condition, area=area, session=ses)
            if not lfp_matches: continue
            
            # Use trial-averaged LFP for speed, or trial-by-trial
            lfp = lfp_matches[0] # (trials, channels, time)
            n_trials, n_chans, n_time = lfp.shape
            
            # Focus on omission window (1031-1562)
            lfp_omit = lfp[:, :, 1031:1562]
            
            for ch in range(n_chans):
                # Flatten trials to increase sample size for PAC
                lfp_ch = lfp_omit[:, ch, :].flatten()
                
                phase, amplitude = extract_phase_amplitude(lfp_ch, fs=1000.0, f_phase=f_phase, f_amp=f_amp)
                mi = compute_modulation_index(phase, amplitude)
                results[area].append(mi)
                
    return results
