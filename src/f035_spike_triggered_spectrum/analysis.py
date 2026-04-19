# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_spike_triggered_spectrum(loader: DataLoader, areas: list, win_ms=200, condition="AXAB"):
    """
    Computes Spike-Triggered Spectrum (STS) for each area.
    """
    results = {}
    
    for area in areas:
        log.info(f"Computing STS for {area} in {condition}")
        units = select_top_units(loader, area, mode="omission", top_n=5)
        
        area_tfr = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            tr, ti = np.where(spk > 0)
            snippets = []
            for t, i in zip(tr, ti):
                if i - win_ms >= 0 and i + win_ms < lfp.shape[1]:
                    snippets.append(lfp[t, i - win_ms : i + win_ms])
            
            if snippets:
                # Compute average TFR of snippets
                f, t, Sxx = scipy.signal.spectrogram(np.mean(snippets, axis=0), fs=1000, nperseg=64, noverlap=32)
                area_tfr.append(Sxx)
                
        if area_tfr:
            results[area] = {
                "f": f,
                "t": t - (win_ms/1000.0), # Center at 0
                "z": np.mean(area_tfr, axis=0)
            }
            
    return results
