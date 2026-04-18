# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def compute_sliding_fano(spk_arr: np.ndarray, window_ms: int = 50, fs: float = 1000.0):
    """
    Computes Fano Factor (Var/Mean) using a sliding window.
    spk_arr: (trials, units, time)
    Returns: (units, time)
    """
    n_trials, n_units, n_time = spk_arr.shape
    win_samples = int(window_ms * (fs / 1000.0))
    
    # 1. Boxcar summation for counts in window
    from scipy.ndimage import uniform_filter1d
    # filter along time axis (-1)
    counts = uniform_filter1d(spk_arr.astype(float), size=win_samples, axis=-1) * win_samples
    
    # 2. Var and Mean across trials
    var = np.var(counts, axis=0)
    mean = np.mean(counts, axis=0)
    
    # FF = Var / Mean
    # Add epsilon to mean to avoid div by zero
    ff = var / (mean + 1e-10)
    
    return ff

def analyze_fano_factor(loader: DataLoader, sessions: list, areas: list, condition="AXAB"):
    """
    Analyzes Fano Factor trajectories across areas.
    """
    results = {area: [] for area in areas}
    
    for ses in sessions:
        log.info(f"Analyzing Fano Factor for Session: {ses}")
        for area in areas:
            spk_matches = loader.get_signal(mode="spk", condition=condition, area=area, session=ses)
            if not spk_matches: continue
            
            spk = spk_matches[0]
            # Compute FF over time (sliding 50ms)
            ff = compute_sliding_fano(spk, window_ms=50)
            
            # Average across units for population summary
            results[area].append(np.mean(ff, axis=0))
            
    # Final aggregation: average across sessions
    final_results = {}
    for area in areas:
        if results[area]:
            final_results[area] = np.mean(results[area], axis=0)
            
    return final_results
