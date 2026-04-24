# beta
import numpy as np
from scipy.ndimage import gaussian_filter1d
from sklearn.decomposition import PCA
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_pca_trajectories(loader: DataLoader, sessions: list, area: str):
    """
    Computes population state-space trajectories (PCA) for Standard vs Omission.
    """
    results = {}
    
    for ses in sessions:
        print(f"[action] Analyzing PCA Trajectories for Session: {ses} in {area}")
        log.info(f"Analyzing PCA Trajectories for Session: {ses} in {area}")
        
        # Load conditions: Standard (AAAB) and Omission (AXAB)
        spk_std = loader.get_signal(mode="spk", condition="AAAB", area=area, session=ses, align_to="p1")
        spk_omit = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses, align_to="p1")
        
        if not spk_std or not spk_omit: 
            print(f"[warning] Data missing for session {ses}, skipping.")
            continue
        
        # spk_std is a list of (trials, units, time) matrices
        # get the first session matrix
        s_std = spk_std[0]
        s_omit = spk_omit[0]
        
        print(f"[action] Shapes - Standard: {s_std.shape}, Omission: {s_omit.shape}")
        
        # Average PSTH for all units (units, time)
        # Multiply by 1000 to get spikes/sec (Hz)
        psth_std = np.mean(s_std, axis=0) * 1000.0
        psth_omit = np.mean(s_omit, axis=0) * 1000.0
        
        # Smooth the PSTHs to get continuous trajectories
        sigma_ms = 30
        print(f"[action] Applying Gaussian smoothing (sigma={sigma_ms}ms)")
        psth_std = gaussian_filter1d(psth_std, sigma=sigma_ms, axis=1)
        psth_omit = gaussian_filter1d(psth_omit, sigma=sigma_ms, axis=1)
        
        # Concatenate for global PCA fit
        X = np.hstack([psth_std, psth_omit]).T # (time*2, units)
        print(f"[action] PCA input shape: {X.shape}")
        
        # Limit to 3 components, requires at least 3 units
        n_units = X.shape[1]
        if n_units < 3:
            print(f"[warning] Too few units ({n_units}) for PCA in session {ses}, skipping.")
            continue
            
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X)
        
        # Split back
        n_t = psth_std.shape[1]
        traj_std = X_pca[:n_t, :]
        traj_omit = X_pca[n_t:, :]
        
        print(f"[result] Session {ses} PCA explained variance: {pca.explained_variance_ratio_}")
        
        results[ses] = {
            'std': traj_std,
            'omit': traj_omit,
            'explained_var': pca.explained_variance_ratio_
        }
        
    return results
