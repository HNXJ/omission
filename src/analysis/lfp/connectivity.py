import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests
from src.analysis.io.logger import log

def apply_rate_matching(src_pop, tgt_pop):
    """
    Ensures firing rate matching between populations to prevent rate-driven causality bias.
    Scales the higher-rate population down.
    """
    rate_src = np.mean(src_pop)
    rate_tgt = np.mean(tgt_pop)
    
    if rate_src == 0 or rate_tgt == 0:
        return src_pop, tgt_pop
        
    if rate_src > rate_tgt:
        scale = rate_tgt / rate_src
        src_pop = src_pop * scale
    else:
        scale = rate_src / rate_tgt
        tgt_pop = tgt_pop * scale
        
    return src_pop, tgt_pop

def compute_granger_causality(src_signal, tgt_signal, maxlag=20, verbose=False):
    """
    Computes Directed Flow (Granger) between two signals.
    Automatically handles differencing for stationarity and rate-matching if spiking.
    """
    # 1. First-order differencing for stationarity
    src_diff = np.diff(src_signal)
    tgt_diff = np.diff(tgt_signal)
    
    # 2. Handle zero variance
    if np.var(src_diff) < 1e-9 or np.var(tgt_diff) < 1e-9:
        return 0.0, 1.0, 0 # F, p, lag
    
    # 3. Stack data: tgt is col 0, src is col 1 for tgt ~ src
    data_gc = np.stack([tgt_diff, src_diff], axis=1)
    
    if data_gc.shape[0] < 3 * maxlag:
        log.warning(f"Insufficient observations ({data_gc.shape[0]}) for maxlag={maxlag}")
        return 0.0, 1.0, 0
        
    try:
        gc_res = grangercausalitytests(data_gc, maxlag=maxlag, verbose=verbose)
        
        # Scan all lags, select optimal (minimum p-value)
        best_f = 0.0
        best_p = 1.0
        best_lag = 1
        for lag in range(1, maxlag + 1):
            f_val = gc_res[lag][0]['ssr_ftest'][0]
            p_val = gc_res[lag][0]['ssr_ftest'][1]
            if p_val < best_p:
                best_f = f_val
                best_p = p_val
                best_lag = lag
        
        return best_f, best_p, best_lag
    except Exception as e:
        log.error(f"GC fitting failed: {e}")
        return 0.0, 1.0, 0
