import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_surprise(loader: DataLoader, areas: list):
    """
    Computes population-level Surprise Index across 11 areas.
    Surprise Index = (FR_Omission - FR_Standard) / (FR_Omission + FR_Standard + 1e-6)
    Evaluated in the [0, 500] ms window post-omission onset.
    """
    results = {}
    for area in areas:
        print(f"[action] Computing Surprise Index for area: {area}")
        spk_aaab_list = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        spk_axab_list = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        
        if not spk_aaab_list or not spk_axab_list:
            continue
            
        # Window: 0 to 500 ms post-omission (samples 1000 to 1500)
        start_idx = 1000
        end_idx = 1500
        
        unit_aaab_fr = []
        for arr in spk_aaab_list:
            if arr.size > 0:
                # arr is (trials, units, time)
                mean_over_trials = np.mean(arr[:, :, start_idx:end_idx], axis=0) # (units, time)
                mean_fr = np.mean(mean_over_trials, axis=1) * 1000.0 # (units,)
                unit_aaab_fr.extend(mean_fr)
                
        unit_axab_fr = []
        for arr in spk_axab_list:
            if arr.size > 0:
                mean_over_trials = np.mean(arr[:, :, start_idx:end_idx], axis=0)
                mean_fr = np.mean(mean_over_trials, axis=1) * 1000.0
                unit_axab_fr.extend(mean_fr)
                
        if not unit_aaab_fr or not unit_axab_fr:
            continue
            
        unit_aaab_fr = np.array(unit_aaab_fr)
        unit_axab_fr = np.array(unit_axab_fr)
        
        # Calculate surprise per unit
        # Surprise = (Omission - Standard) / (Omission + Standard)
        denom = unit_axab_fr + unit_aaab_fr
        valid = denom > 1e-5
        
        surprise_indices = (unit_axab_fr[valid] - unit_aaab_fr[valid]) / denom[valid]
        
        if len(surprise_indices) > 0:
            results[area] = {
                'mean': np.mean(surprise_indices),
                'sem': np.std(surprise_indices) / np.sqrt(len(surprise_indices)),
                'n_units': len(surprise_indices)
            }
            print(f"[result] Area {area}: Surprise = {results[area]['mean']:.3f} (n={len(surprise_indices)})")
            
    return results
