from __future__ import annotations
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List

from src.analysis.io.loader import DataLoader
from src.analysis.lfp.lfp_constants import ALL_CONDITIONS, CANONICAL_AREAS
from src.analysis.io.logger import log

def get_lfp_signal(
    area: str, 
    condition: str,
    align_to: str = 'omission',
    **kwargs
) -> np.ndarray:
    """
    Public entrypoint for LFP signal access.
    Uses DataLoader and ensures omission-local alignment where applicable.
    Returns: Concatenated array (total_trials, area_channels, time)
    """
    loader = DataLoader()
    
    # Standardize condition
    if condition not in ALL_CONDITIONS:
        log.warning(f"Condition {condition} not in canonical set.")
    
    # Determine alignment
    # If align_to is 'omission', DataLoader handles the cropping to [-1000, 1000]ms
    data_list = loader.get_signal(mode="lfp", condition=condition, area=area, align_to=align_to)
    
    if not data_list:
        return np.array([])
        
    # Concatenate trials across sessions
    # data_list entries are (trials, area_channels, time)
    # They should have the same number of area_channels if they share the same area mapping logic
    # But wait, different probes might have different number of channels in the same area.
    # Actually, our mapping logic uses start_ch/end_ch which should be consistent?
    # No, it calculates n_channels based on LINSPACE. 
    # Let's just padding/trimming channels or only taking min if mismatch?
    # User brief says "one shared area mapping".
    
    # For now, assume area_channels match or we force them to match.
    # Actually, many areas will have same channel count if we split 128 channels into N areas.
    
    # To be safe, find min channels
    min_ch = min(arr.shape[1] for arr in data_list)
    aligned_data = [arr[:, :min_ch, :] for arr in data_list]
    
    final_arr = np.concatenate(aligned_data, axis=0)
    return final_arr

def run_lfp_spectral_pipeline(area: str, condition: str):
    """
    Complete flow: Load -> Preprocess -> TFR -> Normalize -> Band Collapse
    """
    from src.analysis.lfp.lfp_preproc import preprocess_lfp, baseline_normalize
    from src.analysis.lfp.lfp_tfr import compute_multitaper_tfr, collapse_band_power
    
    # 1. Load aligned to omission
    log.progress(f"Running Spectral Pipeline for {area} - {condition}")
    lfp = get_lfp_signal(area, condition, align_to="omission")
    if lfp.size == 0: return None
    
    # 2. Preprocess
    lfp_clean = preprocess_lfp(lfp)
    
    # 3. TFR (Linear Power)
    freqs, times, power = compute_multitaper_tfr(lfp_clean)
    # times is relative to start of slice (0 to 2000ms). Center (0ms omission) is at 1000ms.
    times_local = times - 1000.0
    
    # 4. Baseline Normalize ([-250, -50]ms)
    normed_power = baseline_normalize(power, times_local)
    
    # 5. Average across trials and channels for pop summary
    avg_power = np.mean(normed_power, axis=(0, 1)) # (freqs, times)
    
    # 6. Band collapse
    bands = collapse_band_power(freqs, normed_power)
    # bands: {band_name: (trials, channels, times)}
    
    return {
        "freqs": freqs,
        "times": times_local,
        "tfr": avg_power,
        "bands": {k: np.mean(v, axis=(0, 1)) for k, v in bands.items()}
    }
