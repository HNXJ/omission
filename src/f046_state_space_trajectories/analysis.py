import numpy as np
from sklearn.decomposition import PCA
from scipy.ndimage import gaussian_filter1d
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_state_space(areas: list, sigma_ms=50):
    """
    Computes 3D PCA state-space trajectories for AAAB (Stimulus) vs AXAB (Omission).
    """
    loader = DataLoader()
    results = {}
    
    MIN_FR_HZ = 1.0
    
    for area in areas:
        log.progress(f"Analyzing State-Space Trajectories for {area}")
        
        spk_axab = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        spk_aaab = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        
        if not spk_axab or not spk_aaab:
            continue
            
        area_entries = loader.area_map.get(area, [])
        all_units_ax = []
        all_units_aa = []
        
        for i, entry in enumerate(area_entries):
            ses = entry["session"]
            if ses in loader.BLACKLISTED_SESSIONS:
                continue
                
            try:
                arr_ax = spk_axab[i]
                arr_aa = spk_aaab[i]
            except IndexError:
                continue
                
            if arr_ax.size == 0 or arr_aa.size == 0: continue
            
            # Average across trials
            psth_ax = np.mean(arr_ax, axis=0) * 1000 # (units, time)
            psth_aa = np.mean(arr_aa, axis=0) * 1000 # (units, time)
            
            win_stim = slice(0, 500)     # -1000 to -500 relative to omission
            win_omit = slice(1000, 1500) # 0 to +500 relative to omission
            
            fr_ax_stim = np.mean(psth_ax[:, win_stim], axis=1)
            fr_ax_omit = np.mean(psth_ax[:, win_omit], axis=1)
            
            stable_mask = (np.maximum(fr_ax_stim, fr_ax_omit) > MIN_FR_HZ)
            
            if np.any(stable_mask):
                # Apply Gaussian smoothing for continuous trajectories
                smooth_ax = gaussian_filter1d(psth_ax[stable_mask], sigma=sigma_ms, axis=1)
                smooth_aa = gaussian_filter1d(psth_aa[stable_mask], sigma=sigma_ms, axis=1)
                all_units_ax.append(smooth_ax)
                all_units_aa.append(smooth_aa)
                
        if not all_units_ax:
            continue
            
        pop_ax = np.concatenate(all_units_ax, axis=0) # (total_units, time)
        pop_aa = np.concatenate(all_units_aa, axis=0) # (total_units, time)
        
        # Need at least 3 units for 3D PCA
        if pop_ax.shape[0] < 3:
            log.warning(f"Not enough stable units in {area} for 3D PCA.")
            continue
            
        # Normalize each unit (Z-score) to prevent high firing rate units from dominating PCA
        X_unified = np.concatenate([pop_aa, pop_ax], axis=1) # (N, 2T)
        means = np.mean(X_unified, axis=1, keepdims=True)
        stds = np.std(X_unified, axis=1, keepdims=True)
        stds[stds == 0] = 1.0 # prevent division by zero
        X_unified_norm = (X_unified - means) / stds
        
        # PCA requires (samples, features) -> (2T, N)
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X_unified_norm.T) # (2T, 3)
        
        var_explained = pca.explained_variance_ratio_
        log.info(f"  {area} PCA Variance Explained: {np.sum(var_explained)*100:.1f}% (PC1: {var_explained[0]*100:.1f}%, PC2: {var_explained[1]*100:.1f}%, PC3: {var_explained[2]*100:.1f}%)")
        
        # Split back into conditions
        T = pop_aa.shape[1]
        traj_aa = X_pca[:T, :]
        traj_ax = X_pca[T:, :]
        
        results[area] = {
            "traj_aa": traj_aa,
            "traj_ax": traj_ax,
            "var_explained": var_explained,
            "n_units": pop_ax.shape[0]
        }
        
    return results