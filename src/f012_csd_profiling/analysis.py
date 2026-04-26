import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def compute_csd(lfp, sigma=0.4, spacing=0.01):
    """
    Computes Current Source Density (CSD) using the 2nd spatial derivative.
    lfp: (channels, time)
    """
    n_ch = lfp.shape[0]
    csd = np.zeros_like(lfp)
    
    # 2nd spatial derivative approximation
    # CSD(c) = -sigma * (V(c-1) - 2V(c) + V(c+1)) / (spacing^2)
    for c in range(1, n_ch - 1):
        csd[c] = -sigma * (lfp[c-1] - 2*lfp[c] + lfp[c+1]) / (spacing**2)
        
    return csd

def align_to_layer4(csd_data, l4_idx, target_length=60):
    center = target_length // 2
    aligned = np.full((target_length, csd_data.shape[1]), np.nan)
    
    n_ch = csd_data.shape[0]
    
    start_in_aligned = center - l4_idx
    end_in_aligned = start_in_aligned + n_ch
    
    start_in_csd = 0
    end_in_csd = n_ch
    
    if start_in_aligned < 0:
        start_in_csd = -start_in_aligned
        start_in_aligned = 0
        
    if end_in_aligned > target_length:
        end_in_csd = n_ch - (end_in_aligned - target_length)
        end_in_aligned = target_length
        
    if start_in_aligned < end_in_aligned and start_in_csd < end_in_csd:
        aligned[start_in_aligned:end_in_aligned, :] = csd_data[start_in_csd:end_in_csd, :]
        
    return aligned

def run_f012_analysis():
    loader = DataLoader()
    areas = list(loader.area_map.keys())
    results = {}
    
    target_ch = 60
    
    for area in areas:
        log.progress(f"Computing CSD Profiling for {area}")
        lfp_list = loader.get_signal(mode="lfp", condition="AXAB", area=area, align_to="omission", pre_ms=2000, post_ms=2000)
        
        if not lfp_list: continue
        
        aligned_csds = []
        for lfp_arr in lfp_list:
            if lfp_arr.shape[-1] < 4000: continue
            
            # 1. Trial average LFP
            mean_lfp = np.mean(lfp_arr, axis=0) # (channels, time)
            
            # 2. Compute CSD
            csd = compute_csd(mean_lfp)
            
            # 3. Identify L4 sink (earliest strong negative deflection)
            # P1 onset is 969. Use 969 to 1069 window. Strongest sink = minimum CSD value
            p1_win = slice(969, 1069)
            csd_p1 = np.mean(csd[:, p1_win], axis=1)
            # Find the channel with the minimum CSD (strongest sink)
            l4_idx = np.argmin(csd_p1)
            
            # 4. Align
            aligned = align_to_layer4(csd, l4_idx, target_length=target_ch)
            aligned_csds.append(aligned)
            
        if aligned_csds:
            pop_csd = np.nanmean(np.array(aligned_csds), axis=0)
            results[area] = pop_csd
            
    return results