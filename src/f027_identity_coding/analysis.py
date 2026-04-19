# beta
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def decode_omission_identity(spk_omit1: np.ndarray, spk_omit2: np.ndarray, win_ms: int = 100, step_ms: int = 50, fs: float = 1000.0):
    """
    Decodes Omission-of-A vs Omission-of-B.
    spk_omit1: (trials, units, time) - AXAB
    spk_omit2: (trials, units, time) - BXBA
    """
    n_trials1, n_units, n_time = spk_omit1.shape
    n_trials2 = spk_omit2.shape[0]
    
    win_samples = int(win_ms * (fs / 1000.0))
    step_samples = int(step_ms * (fs / 1000.0))
    
    time_bins = np.arange(0, n_time - win_samples, step_samples)
    accuracies = []
    
    model = LogisticRegression(solver='liblinear', max_iter=200)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for t in time_bins:
        X1 = np.sum(spk_omit1[:, :, t:t+win_samples], axis=-1)
        X2 = np.sum(spk_omit2[:, :, t:t+win_samples], axis=-1)
        X = np.vstack([X1, X2])
        y = np.concatenate([np.zeros(n_trials1), np.ones(n_trials2)])
        
        X = X / (np.max(X) + 1e-10)
        
        if n_units > 0:
            scores = cross_val_score(model, X, y, cv=cv)
            accuracies.append(np.mean(scores))
        else:
            accuracies.append(0.5)
            
    return time_bins + win_samples/2, np.array(accuracies)

def analyze_omission_identity(loader: DataLoader, sessions: list, areas: list):
    """
    Computes identity decoding across areas.
    """
    results = {}
    times = None
    
    for ses in sessions:
        log.info(f"Computing Identity Decoding for {ses}")
        for area in areas:
            # AXAB vs BXBA
            spk1 = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            spk2 = loader.get_signal(mode="spk", condition="BXBA", area=area, session=ses)
            
            if not spk1 or not spk2: continue
            
            t_pts, acc = decode_omission_identity(spk1[0], spk2[0])
            if times is None: times = t_pts
            
            if area not in results: results[area] = []
            results[area].append(acc)
            
    # Aggregate
    final_results = {}
    for area in areas:
        if area in results:
            arr = np.array(results[area])
            final_results[area] = {
                'mean': np.mean(arr, axis=0),
                'sem': np.std(arr, axis=0) / np.sqrt(len(arr))
            }
            
    return times, final_results
