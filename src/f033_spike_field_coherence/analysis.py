# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_spike_field_coherence(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes Spike-Field Coherence (SFC) spectrum using multi-taper or Welch proxy.
    """
    results = {}
    
    for area in areas:
        log.info(f"Computing SFC for {area} in {condition}")
        units = select_top_units(loader, area, mode="omission", top_n=5)
        
        area_coh = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            # Welch-based coherence proxy
            # Average across trials
            coh_trials = []
            for tr in range(lfp.shape[0]):
                f, Cxy = scipy.signal.coherence(lfp[tr], spk[tr], fs=1000, nperseg=256)
                coh_trials.append(Cxy)
                
            area_coh.append(np.mean(coh_trials, axis=0))
            
        if area_coh:
            results[area] = {
                "freqs": f,
                "coh_mean": np.mean(area_coh, axis=0),
                "coh_sem": np.std(area_coh, axis=0) / np.sqrt(len(area_coh))
            }
            
    return results
