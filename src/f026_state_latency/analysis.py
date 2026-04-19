# beta
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def compute_divergence_latency(loader, spk_std: np.ndarray, spk_omit: np.ndarray, condition="AXAB", win_ms: int = 50, step_ms: int = 10, fs: float = 1000.0):
    """
    Finds the first time point where Standard vs Omission decoding accuracy is significantly above chance.
    spk: (trials, units, time)
    Returns: latency_ms, times, accuracies, threshold
    """
    n_trials_s, n_units, n_time = spk_std.shape
    n_trials_o = spk_omit.shape[0]
    
    win_samples = int(win_ms * (fs / 1000.0))
    step_samples = int(step_ms * (fs / 1000.0))
    
    time_bins = np.arange(0, n_time - win_samples, step_samples)
    accuracies = []
    
    model = LogisticRegression(solver='liblinear', max_iter=200)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for t in time_bins:
        X1 = np.sum(spk_std[:, :, t:t+win_samples], axis=-1)
        X2 = np.sum(spk_omit[:, :, t:t+win_samples], axis=-1)
        X = np.vstack([X1, X2])
        y = np.concatenate([np.zeros(n_trials_s), np.ones(n_trials_o)])
        
        # Norm
        X = X / (np.max(X) + 1e-10)
        
        scores = cross_val_score(model, X, y, cv=cv)
        accuracies.append(np.mean(scores))
        
    accuracies = np.array(accuracies)
    times = time_bins + win_samples/2
    
    # Simple thresholding for latency (0.6 or 0.7 for significance)
    # Better: Shuffled baseline
    threshold = 0.65 
    sig_idx = np.where(accuracies > threshold)[0]
    
    # Latency from omission onset
    omission_onset = loader.get_omission_onset(condition)
    if len(sig_idx) > 0:
        latency = times[sig_idx[0]] - omission_onset
    else:
        latency = np.nan
        
    return latency, times - omission_onset, accuracies, threshold

def analyze_area_latencies(loader: DataLoader, sessions: list, areas: list, condition="AXAB"):
    """
    Computes divergence latencies for multiple areas.
    """
    results = {}
    for area in areas:
        log.info(f"Computing Latency for {area}")
        area_accs = []
        area_latencies = []
        
        for ses in sessions:
            spk_std = loader.get_signal(mode="spk", condition="AAAB", area=area, session=ses)
            spk_omit = loader.get_signal(mode="spk", condition=condition, area=area, session=ses)
            
            if not spk_std or not spk_omit: continue
            
            lat, times, acc, thresh = compute_divergence_latency(loader, spk_std[0], spk_omit[0], condition=condition)
            if not np.isnan(lat):
                area_latencies.append(lat)
            area_accs.append(acc)
            
        if area_accs:
            results[area] = {
                'latency_mean': np.mean(area_latencies) if area_latencies else np.nan,
                'latency_std': np.std(area_latencies) if area_latencies else 0,
                'times': times,
                'accuracy_mean': np.mean(area_accs, axis=0)
            }
            
    return results
