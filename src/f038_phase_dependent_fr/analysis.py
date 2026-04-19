# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_phase_dependent_fr(loader: DataLoader, areas: list, freq_band=(13, 30), condition="AXAB"):
    """
    Computes Phase-Dependent Firing Rate (PDFR).
    How firing rate varies with LFP phase in a specific band.
    """
    results = {}
    n_bins = 18
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    
    for area in areas:
        log.info(f"Computing PDFR ({freq_band}Hz) for {area}")
        units = select_top_units(loader, area, mode="omission", top_n=5)
        
        area_dist = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            # Filter LFP for phase
            nyq = 500.0
            b, a = scipy.signal.butter(4, [freq_band[0]/nyq, freq_band[1]/nyq], btype='bandpass')
            filt = scipy.signal.filtfilt(b, a, lfp, axis=-1)
            phase = np.angle(scipy.signal.hilbert(filt, axis=-1))
            
            # Bin phases at spike times
            spike_phases = phase[np.where(spk > 0)]
            counts, _ = np.histogram(spike_phases, bins=bins)
            # Normalize to get relative rate
            if np.sum(counts) > 0:
                area_dist.append(counts / np.mean(counts))
                
        if area_dist:
            results[area] = {
                "bins": (bins[:-1] + bins[1:]) / 2,
                "dist_mean": np.mean(area_dist, axis=0),
                "dist_sem": np.std(area_dist, axis=0) / np.sqrt(len(area_dist))
            }
            
    return results
