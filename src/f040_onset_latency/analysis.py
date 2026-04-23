# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def detect_onset(times, psth, threshold_sigma=3.0, min_consecutive=3):
    """
    Detects the onset of response.
    times: ms from omission
    psth: firing rate array
    """
    # Baseline: -200 to 0ms
    baseline_idx = (times >= -200) & (times <= 0)
    if not np.any(baseline_idx):
        return None
        
    mu = np.mean(psth[baseline_idx])
    sigma = np.std(psth[baseline_idx])
    
    thresh = mu + threshold_sigma * sigma
    print(f"DEBUG: mu={mu:.4f}, sigma={sigma:.4f}, thresh={thresh:.4f}, max_post={np.max(psth[times > 0]):.4f}")
    above = psth > thresh
    
    # Search post-omission (skip first 50ms to avoid off-transients)
    post_idx = np.where(times > 50)[0]
    for i in range(len(post_idx) - min_consecutive):
        idx = post_idx[i]
        if np.all(above[idx : idx + min_consecutive]):
            return times[idx]
            
    return None

def analyze_onset_latency(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes population onset latency per area.
    """
    results = {}
    
    for area in areas:
        log.info(f"Analyzing Onset Latency for {area} in {condition}")
        # Use get_signal with align_to="omission"
        spk_list = loader.get_signal(mode="spk", condition=condition, area=area, align_to="omission")
        
        if not spk_list:
            log.warning(f"No data for {area}")
            continue
            
        # Population PSTH: mean across trials, units, and then sessions
        # Each s is (n_trials, n_units, n_times)
        session_psths = []
        for s in spk_list:
            # s is (trials, units, time)
            # FR (Hz) = mean(trials, units) * 1000
            psth = np.mean(s, axis=(0, 1)) * 1000
            session_psths.append(psth)
            
        pop_psth = np.mean(np.stack(session_psths), axis=0)
        
        # SMOOTHING: 20ms Gaussian window
        from scipy.ndimage import gaussian_filter1d
        pop_psth = gaussian_filter1d(pop_psth, sigma=20) # 20ms sigma
        
        times = np.linspace(-1000, 1000, len(pop_psth))
        
        latency = detect_onset(times, pop_psth, threshold_sigma=2.0, min_consecutive=10)
        
        results[area] = {
            "times": times,
            "psth": pop_psth,
            "latency": latency
        }
        log.info(f"Area {area} Latency: {latency} ms")
        
    return results
