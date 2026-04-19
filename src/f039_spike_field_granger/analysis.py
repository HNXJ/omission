# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_spike_field_granger(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes Directed Information Flow between SPK and LFP.
    Proxy: Lagged Cross-Correlation Peak Direction.
    """
    results = {}
    
    for area in areas:
        log.info(f"Computing SPK-LFP Granger for {area}")
        units = select_top_units(loader, area, mode="omission", top_n=5)
        
        all_lags = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            # Cross-Correlation between binary spikes and LFP envelope
            env = np.abs(scipy.signal.hilbert(lfp, axis=-1))
            
            xcorr_trials = []
            for tr in range(lfp.shape[0]):
                # Normalize
                s = spk[tr] - np.mean(spk[tr])
                e = env[tr] - np.mean(env[tr])
                if np.std(s) > 1e-10 and np.std(e) > 1e-10:
                    xcorr = scipy.signal.correlate(s, e, mode='full')
                    lags = scipy.signal.correlation_lags(len(s), len(e), mode='full')
                    xcorr_trials.append(xcorr / (len(s) * np.std(s) * np.std(e)))
            
            if xcorr_trials:
                all_lags.append(np.mean(xcorr_trials, axis=0))
                
        if all_lags:
            results[area] = {
                "lags": lags,
                "xcorr_mean": np.mean(all_lags, axis=0),
                "xcorr_sem": np.std(all_lags, axis=0) / np.sqrt(len(all_lags))
            }
            
    return results
