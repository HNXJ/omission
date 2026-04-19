# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.lfp_pipeline import get_lfp_signal
from src.analysis.lfp.lfp_preproc import preprocess_lfp

def compute_directed_mi(source_arr, target_arr, tau_ms=50):
    """
    Computes Directed Mutual Information (Transfer Entropy proxy).
    I(Source_past ; Target_present | Target_past)
    Simplified here as I(Source_past ; Target_present).
    """
    from sklearn.decomposition import PCA
    # Flatten across channels
    s = np.mean(source_arr, axis=1) # (trials, time)
    t = np.mean(target_arr, axis=1) # (trials, time)
    
    # Shift source by tau
    tau = int(tau_ms)
    s_past = s[:, :-tau]
    t_pres = t[:, tau:]
    
    # Compute correlation as MI proxy
    corrs = []
    for tr in range(s.shape[0]):
        if np.std(s_past[tr]) > 1e-10 and np.std(t_pres[tr]) > 1e-10:
            corrs.append(np.corrcoef(s_past[tr], t_pres[tr])[0, 1])
            
    if not corrs: return 0.0
    rho = np.mean(corrs)
    rho = np.clip(rho, -0.99, 0.99)
    mi = -0.5 * np.log(1 - rho**2)
    return mi

def analyze_directed_flow(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes directed flow matrix between all areas during omission.
    """
    n = len(areas)
    flow_mat = np.zeros((n, n))
    
    # Load all LFPs once
    lfps = {}
    for area in areas:
        raw = get_lfp_signal(area, condition, align_to="omission")
        if raw.size > 0:
            lfps[area] = preprocess_lfp(raw)[:, :, 1000:1531] # Omission window
            
    for i, a_src in enumerate(areas):
        for j, a_tgt in enumerate(areas):
            if i != j and a_src in lfps and a_tgt in lfps:
                log.info(f"Computing Directed Flow: {a_src} -> {a_tgt}")
                flow_mat[i, j] = compute_directed_mi(lfps[a_src], lfps[a_tgt])
                
    return flow_mat
