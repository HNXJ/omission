# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_area_psths(loader: DataLoader, areas: list):
    """
    Computes area-level average PSTHs for Standard and Omission conditions.
    """
    results = {}
    for area in areas:
        log.info(f"Computing PSTH for {area}")
        spk_aaab_list = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        spk_axab_list = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        
        if not spk_aaab_list or not spk_axab_list: continue
        
        psths_aaab = np.vstack([np.mean(arr, axis=0) for arr in spk_aaab_list])
        psths_axab = np.vstack([np.mean(arr, axis=0) for arr in spk_axab_list])
        
        results[area] = {
            'aaab': np.mean(psths_aaab, axis=0) * 1000.0,
            'aaab_sem': (np.std(psths_aaab, axis=0) / np.sqrt(len(psths_aaab))) * 1000.0,
            'axab': np.mean(psths_axab, axis=0) * 1000.0,
            'axab_sem': (np.std(psths_axab, axis=0) / np.sqrt(len(psths_axab))) * 1000.0,
            'n_units': len(psths_aaab)
        }
    return results
