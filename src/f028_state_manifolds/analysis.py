# beta
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def compute_manifold_coupling(pop1: np.ndarray, pop2: np.ndarray, n_comp: int = 3):
    """
    Computes CCA between two populations.
    pop: (time, units)
    """
    # 1. PCA to reduce noise
    pca1 = PCA(n_components=n_comp); pca2 = PCA(n_components=n_comp)
    X1 = pca1.fit_transform(pop1); X2 = pca2.fit_transform(pop2)
    
    # 2. CCA
    cca = CCA(n_components=1)
    X1_c, X2_c = cca.fit_transform(X1, X2)
    
    corr = np.corrcoef(X1_c.T, X2_c.T)[0, 1]
    return corr, X1_c, X2_c

def analyze_cross_area_manifolds(loader: DataLoader, sessions: list, areas: list, condition="AXAB"):
    """
    Computes pairwise manifold coupling (CCA correlation) during omission.
    """
    n = len(areas)
    coupling_mat = np.zeros((n, n))
    
    for ses in sessions:
        log.info(f"Computing Manifold Coupling for {ses}")
        pops = {}
        for area in areas:
            spk = loader.get_signal(mode="spk", condition=condition, area=area, session=ses)
            if not spk: continue
            # Average across trials, focus on omission window (1000:2500)
            pops[area] = np.mean(spk[0], axis=0).T[1000:2500, :]
            
        for i, a1 in enumerate(areas):
            for j, a2 in enumerate(areas):
                if a1 in pops and a2 in pops and i != j:
                    corr, _, _ = compute_manifold_coupling(pops[a1], pops[a2])
                    coupling_mat[i, j] += corr
                    
    coupling_mat /= len(sessions)
    return coupling_mat
