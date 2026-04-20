# core
import numpy as np
from sklearn.decomposition import PCA
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_population_manifolds(loader: DataLoader, areas: list):
    """
    Computes 3D PCA trajectories with 95% CI bootstrapped confidence tubes.
    """
    results = {}
    for area in areas:
        print(f"""[action] Starting bootstrap manifold analysis for area {area}""")
        spk_aaab = loader.get_signal(mode="spk", condition="AAAB", area=area)
        spk_axab = loader.get_signal(mode="spk", condition="AXAB", area=area)
        
        if not spk_aaab or not spk_axab: continue
        
        # Helper to get bootstrapped mean trajectories
        def get_bootstrapped_traj(spk_data, n_boot=100):
            print(f"""[action] Performing {n_boot} bootstrap iterations""")
            n_trials = len(spk_data)
            trajs = []
            for i in range(n_boot):
                idx = np.random.choice(n_trials, n_trials, replace=True)
                sample = np.vstack([np.mean(spk_data[j], axis=0) for j in idx]).T
                trajs.append(sample)
            return np.array(trajs)

        # Concatenate and PCA
        t_idx = slice(500, 3000, 10)
        pop_aaab = get_bootstrapped_traj(spk_aaab)[:, t_idx, :]
        pop_axab = get_bootstrapped_traj(spk_axab)[:, t_idx, :]
        
        # Project all through common PCA
        mean_aaab = np.mean(pop_aaab, axis=0)
        mean_axab = np.mean(pop_axab, axis=0)
        X_combined = np.vstack([mean_aaab, mean_axab])
        
        pca = PCA(n_components=3)
        pca.fit(X_combined)
        
        # Project bootstraps
        proj_aaab = np.array([pca.transform(traj) for traj in pop_aaab])
        proj_axab = np.array([pca.transform(traj) for traj in pop_axab])
        
        results[area] = {
            'traj_aaab': np.mean(proj_aaab, axis=0),
            'ci_aaab': np.percentile(proj_aaab, [2.5, 97.5], axis=0),
            'traj_axab': np.mean(proj_axab, axis=0),
            'ci_axab': np.percentile(proj_axab, [2.5, 97.5], axis=0),
            'explained_var': pca.explained_variance_ratio_
        }
        print(f"""[action] Completed manifold analysis for {area}""")
    return results
