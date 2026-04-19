# beta
import numpy as np
from sklearn.decomposition import PCA
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_pca_trajectories(loader: DataLoader, sessions: list, area: str):
    """
    Computes population state-space trajectories (PCA) for Stim vs Omission.
    """
    results = {}
    
    for ses in sessions:
        log.info(f"Analyzing PCA Trajectories for Session: {ses} in {area}")
        
        # Load conditions: Standard (AAAB) and Omission (AXAB)
        spk_std = loader.get_signal(mode="spk", condition="AAAB", area=area, session=ses)
        spk_omit = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
        
        if not spk_std or not spk_omit: continue
        
        # Average PSTH for all units (units, time)
        psth_std = np.mean(spk_std[0], axis=0) * 1000.0
        psth_omit = np.mean(spk_omit[0], axis=0) * 1000.0
        
        # Concatenate for global PCA fit
        X = np.hstack([psth_std, psth_omit]).T # (time*2, units)
        
        # PCA to 3 components
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X)
        
        # Split back
        n_t = psth_std.shape[1]
        traj_std = X_pca[:n_t, :]
        traj_omit = X_pca[n_t:, :]
        
        results[ses] = {
            'std': traj_std,
            'omit': traj_omit,
            'explained_var': pca.explained_variance_ratio_
        }
        
    return results
