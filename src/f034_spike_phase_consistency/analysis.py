# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def calculate_ppc(phases):
    """
    Computes Pairwise Phase Consistency (PPC).
    PPC = sum_{i,j, i!=j} cos(theta_i - theta_j) / (N*(N-1))
    """
    n = len(phases)
    if n < 2: return 0.0
    
    # Efficient calculation via complex dot product
    complex_phases = np.exp(1j * phases)
    dot_sum = np.abs(np.sum(complex_phases))**2 - n
    return dot_sum / (n * (n - 1))

def analyze_ppc_spectrum(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes PPC Spectrum for each area.
    """
    results = {}
    freqs = np.logspace(np.log10(4), np.log10(80), 12)
    
    for area in areas:
        log.info(f"Computing PPC for {area} in {condition}")
        units = select_top_units(loader, area, mode="omission", top_n=5)
        
        area_ppc = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            unit_spectrum = []
            for f in freqs:
                bw = max(2.0, f * 0.2)
                nyq = 500.0
                b, a = scipy.signal.butter(4, [(f-bw/2)/nyq, (f+bw/2)/nyq], btype='bandpass')
                filt = scipy.signal.filtfilt(b, a, lfp, axis=-1)
                phase = np.angle(scipy.signal.hilbert(filt, axis=-1))
                
                spike_phases = phase[np.where(spk > 0)]
                unit_spectrum.append(calculate_ppc(spike_phases))
            area_ppc.append(unit_spectrum)
            
        if area_ppc:
            results[area] = {
                "freqs": freqs,
                "ppc_mean": np.mean(area_ppc, axis=0),
                "ppc_sem": np.std(area_ppc, axis=0) / np.sqrt(len(area_ppc))
            }
            
    return results
