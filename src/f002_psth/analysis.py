import numpy as np
from scipy.ndimage import gaussian_filter1d
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_area_psths(loader: DataLoader, areas: list):
    """
    Computes area-level average PSTHs for Standard (AAAB) and Omission (AXAB) conditions.
    Applies Gaussian smoothing.
    """
    results = {}
    for area in areas:
        log.info(f"Computing PSTH for {area}")
        print(f"[action] Computing PSTH for area: {area}")
        spk_aaab_list = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        spk_axab_list = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        
        if not spk_aaab_list or not spk_axab_list:
            print(f"[warning] Data missing for {area}, skipping.")
            continue
        
        aaab_unit_means = []
        for arr in spk_aaab_list:
            if arr.size > 0:
                aaab_unit_means.append(np.mean(arr, axis=0)) # (units, time)
        
        axab_unit_means = []
        for arr in spk_axab_list:
            if arr.size > 0:
                axab_unit_means.append(np.mean(arr, axis=0))
                
        if not aaab_unit_means or not axab_unit_means:
            continue
            
        psths_aaab = np.vstack(aaab_unit_means) * 1000.0 # Convert to Hz
        psths_axab = np.vstack(axab_unit_means) * 1000.0
        
        n_units = psths_aaab.shape[0]
        
        # Smooth per unit
        sigma_ms = 30
        psths_aaab_smooth = gaussian_filter1d(psths_aaab, sigma=sigma_ms, axis=1)
        psths_axab_smooth = gaussian_filter1d(psths_axab, sigma=sigma_ms, axis=1)
        
        results[area] = {
            'aaab': np.mean(psths_aaab_smooth, axis=0),
            'aaab_sem': np.std(psths_aaab_smooth, axis=0) / np.sqrt(n_units),
            'axab': np.mean(psths_axab_smooth, axis=0),
            'axab_sem': np.std(psths_axab_smooth, axis=0) / np.sqrt(n_units),
            'n_units': n_units
        }
        print(f"[result] Area {area} PSTH computed for {n_units} units.")
        
    return results
