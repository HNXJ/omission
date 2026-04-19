# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_population_sync_index(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes Population Synchronization Index (PSI).
    Mean PLV of the entire population to local LFP.
    """
    results = {}
    
    for area in areas:
        log.info(f"Computing PSI for {area}")
        units = select_top_units(loader, area, mode="omission", top_n=20)
        
        # Calculate PLV for each unit and average
        all_plvs = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            # Use Beta band (13-30Hz) as default for PSI comparison
            nyq = 500.0
            b, a = scipy.signal.butter(4, [13/nyq, 30/nyq], btype='bandpass')
            filt = scipy.signal.filtfilt(b, a, lfp, axis=-1)
            phase = np.angle(scipy.signal.hilbert(filt, axis=-1))
            
            spike_phases = phase[np.where(spk > 0)]
            if len(spike_phases) > 0:
                plv = np.abs(np.mean(np.exp(1j * spike_phases)))
                all_plvs.append(plv)
                
        if all_plvs:
            results[area] = {
                "psi": np.mean(all_plvs),
                "psi_std": np.std(all_plvs)
            }
            
    return results
