# core
import numpy as np
from sklearn.decomposition import PCA
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_population_manifolds(loader: DataLoader, areas: list):
    """
    Computes 3D PCA trajectories for Standard vs Omission.
    """
    results = {}
    for area in areas:
        log.info(f"Computing PCA manifold for {area}")
        spk_aaab = loader.get_signal(mode="spk", condition="AAAB", area=area)
        spk_axab = loader.get_signal(mode="spk", condition="AXAB", area=area)
        
        if not spk_aaab or not spk_axab: continue
        
        pop_aaab = np.vstack([np.mean(arr, axis=0) for arr in spk_aaab]).T
        pop_axab = np.vstack([np.mean(arr, axis=0) for arr in spk_axab]).T
        
        # Subsample indices (500:3000, step 10)
        t_idx = slice(500, 3000, 10)
        X_combined = np.vstack([pop_aaab[t_idx, :], pop_axab[t_idx, :]])
        
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X_combined)
        
        n_pts = pop_aaab[t_idx, :].shape[0]
        results[area] = {
            'traj_aaab': X_pca[:n_pts, :],
            'traj_axab': X_pca[n_pts:, :],
            'explained_var': pca.explained_variance_ratio_
        }
    return results
