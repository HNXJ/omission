import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from src.analysis.io.logger import log

def sliding_window_decoder(data_cond1: np.ndarray, data_cond2: np.ndarray, 
                           win_ms: int = 100, step_ms: int = 50, fs: float = 1000.0,
                           classifier='logistic'):
    """
    Decodes condition 1 vs 2 from population activity over time.
    data_cond: (trials, units/features, time)
    Returns: (times, accuracies)
    """
    n_trials1, n_features, n_time = data_cond1.shape
    n_trials2 = data_cond2.shape[0]
    
    win_samples = int(win_ms * (fs / 1000.0))
    step_samples = int(step_ms * (fs / 1000.0))
    
    time_bins = np.arange(0, n_time - win_samples, step_samples)
    accuracies = []
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    if classifier == 'logistic':
        model = LogisticRegression(max_iter=1000, solver='liblinear')
    else:
        # Fallback or extendable
        model = LogisticRegression(max_iter=1000, solver='liblinear')
    
    for t in time_bins:
        # Feature Extraction: Mean in window
        X1 = np.mean(data_cond1[:, :, t:t+win_samples], axis=-1) 
        X2 = np.mean(data_cond2[:, :, t:t+win_samples], axis=-1)
        
        X = np.vstack([X1, X2])
        y = np.concatenate([np.zeros(n_trials1), np.ones(n_trials2)])
        
        if n_features > 0:
            # Simple scaling
            X_norm = X / (np.max(np.abs(X)) + 1e-10)
            try:
                scores = cross_val_score(model, X_norm, y, cv=cv)
                accuracies.append(np.mean(scores))
            except Exception as e:
                log.error(f"Decoding failed at t={t}: {e}")
                accuracies.append(0.5)
        else:
            accuracies.append(0.5)
            
    return time_bins + win_samples/2, np.array(accuracies)
