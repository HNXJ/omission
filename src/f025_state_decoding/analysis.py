# beta
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def sliding_window_decoder(spk_cond1: np.ndarray, spk_cond2: np.ndarray, win_ms: int = 100, step_ms: int = 50, fs: float = 1000.0):
    """
    Decodes condition 1 vs 2 from population activity over time.
    spk_cond: (trials, units, time)
    Returns: (times, accuracies)
    """
    n_trials1, n_units, n_time = spk_cond1.shape
    n_trials2 = spk_cond2.shape[0]
    
    win_samples = int(win_ms * (fs / 1000.0))
    step_samples = int(step_ms * (fs / 1000.0))
    
    time_bins = np.arange(0, n_time - win_samples, step_samples)
    accuracies = []
    
    # K-fold cross validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model = LogisticRegression(max_iter=1000, solver='liblinear')
    
    for t in time_bins:
        # 1. Feature Extraction: Sum spikes in window for each unit
        X1 = np.sum(spk_cond1[:, :, t:t+win_samples], axis=-1) # (trials1, units)
        X2 = np.sum(spk_cond2[:, :, t:t+win_samples], axis=-1) # (trials2, units)
        
        X = np.vstack([X1, X2])
        y = np.concatenate([np.zeros(n_trials1), np.ones(n_trials2)])
        
        # 2. Decode
        if n_units > 0:
            # Simple scaling to improve convergence
            X_norm = X / (np.max(X) + 1e-10)
            scores = cross_val_score(model, X_norm, y, cv=cv)
            accuracies.append(np.mean(scores))
        else:
            accuracies.append(0.5)
            
    return time_bins + win_samples/2, np.array(accuracies)

def analyze_state_decoding(loader: DataLoader, sessions: list, areas: list):
    """
    Analyzes decoding accuracy of Standard vs Omission state over time.
    """
    results = {area: [] for area in areas}
    times = None
    
    for ses in sessions:
        log.info(f"Analyzing State Decoding for Session: {ses}")
        for area in areas:
            spk_std = loader.get_signal(mode="spk", condition="AAAB", area=area, session=ses)
            spk_omit = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            
            if not spk_std or not spk_omit: continue
            
            t_pts, acc = sliding_window_decoder(spk_std[0], spk_omit[0], win_ms=100, step_ms=50)
            
            if times is None: times = t_pts
            results[area].append(acc)
            
    # Aggregate across sessions
    final_results = {}
    for area in areas:
        if results[area]:
            final_results[area] = np.mean(results[area], axis=0)
            
    return times, final_results
