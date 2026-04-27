import numpy as np
from scipy.ndimage import gaussian_filter1d
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

CONDITION_GROUPS = {
    "A-Base Sequences": ['AAAB', 'AXAB', 'AAXB', 'AAAX'],
    "B-Base Sequences": ['BBBA', 'BXBA', 'BBXA', 'BBBX'],
    "Random Sequences": ['RRRR', 'RXRR', 'RRXR', 'RRRX']
}

RASTER_CONDS = ['RRRR', 'RXRR', 'RRXR']

def smooth_fr(data, sigma=50):
    """Gaussian convolution for smooth firing rate traces."""
    return gaussian_filter1d(data.astype(float), sigma=sigma)

def analyze_unit_coding(loader: DataLoader, unit_id: str):
    """
    Extracts rasters and PSTHs for a single unit across all 12 sequence conditions.
    """
    print(f"[action] Analyzing coding suite for unit: {unit_id}")
    
    results = {
        'rasters': {},
        'psths': {}
    }
    
    # 1. Rasters
    for cond in RASTER_CONDS:
        spk_data = loader.load_unit_spikes(unit_id, cond)
        if spk_data is not None and spk_data.shape[0] > 0:
            trials, times = np.where(spk_data > 0)
            times_ms = times - 1000  # Shift to p1 onset
            mask = (times_ms >= -1000) & (times_ms <= 4000)
            results['rasters'][cond] = {
                'times': times_ms[mask],
                'trials': trials[mask]
            }

    # 2. PSTHs for all condition groups
    for group_name, conditions in CONDITION_GROUPS.items():
        results['psths'][group_name] = {}
        for cond in conditions:
            spk_data = loader.load_unit_spikes(unit_id, cond)
            if spk_data is None or spk_data.shape[0] == 0:
                continue
                
            n_trials = spk_data.shape[0]
            
            # Firing Rate per trial (Hz)
            fr_trials = spk_data.astype(float) * 1000
            
            # Mean and SEM
            mean_fr = fr_trials.mean(axis=0)
            sem_fr = fr_trials.std(axis=0) / np.sqrt(n_trials)
            
            # NaN/INF Guard: Replace any invalid numbers with 0.0 before smoothing
            mean_fr = np.nan_to_num(mean_fr, nan=0.0, posinf=0.0, neginf=0.0)
            sem_fr = np.nan_to_num(sem_fr, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Gaussian Convolution Smoothing (sigma=50ms)
            mean_smoothed = smooth_fr(mean_fr, sigma=50)
            upper_smoothed = smooth_fr(mean_fr + sem_fr, sigma=50)
            lower_smoothed = smooth_fr(mean_fr - sem_fr, sigma=50)
            
            # Final sanity check: ensure no NaNs survived smoothing
            mean_smoothed = np.nan_to_num(mean_smoothed, nan=0.0)
            upper_smoothed = np.nan_to_num(upper_smoothed, nan=0.0)
            lower_smoothed = np.nan_to_num(lower_smoothed, nan=0.0)
            
            time_ms = np.arange(len(mean_smoothed)) - 1000
            mask = (time_ms >= -1000) & (time_ms <= 4000)
            
            results['psths'][group_name][cond] = {
                'time': time_ms[mask],
                'mean': mean_smoothed[mask],
                'upper': upper_smoothed[mask],
                'lower': lower_smoothed[mask]
            }
            
        # 3. UNIT-LEVEL STATISTICAL PROOF (Significance-Tier Standard)
        # Compare AAAB (Standard) vs AXAB (Omission) in the omission window (969-1500)
        if 'AAAB' in results['psths'][group_name] and 'AXAB' in results['psths'][group_name]:
            from scipy.stats import ranksums
            from src.analysis.stats.tiers import get_significance_tier
            
            # Extract trial data for statistical test
            spk_aaab = loader.load_unit_spikes(unit_id, 'AAAB')
            spk_axab = loader.load_unit_spikes(unit_id, 'AXAB')
            
            if spk_aaab is not None and spk_axab is not None:
                # Window 969 to 1500 (Omission Response)
                win = slice(969, 1500)
                fr_aaab = np.mean(spk_aaab[:, win], axis=1) * 1000.0
                fr_axab = np.mean(spk_axab[:, win], axis=1) * 1000.0
                
                stat, p_val = ranksums(fr_aaab, fr_axab)
                tier_name, k, stars = get_significance_tier(p_val)
                
                results['psths'][group_name]['stats'] = {
                    'p': p_val,
                    'tier': tier_name,
                    'stars': stars,
                    'test': 'Wilcoxon Rank-Sum'
                }
                print(f"[stats] Unit {unit_id} | {group_name} | {tier_name} ({p_val:.2e}) | {stars}")
            
    return results
