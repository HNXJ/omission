# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def fast_pca(data, n_components=3):
    # data: (time, features)
    data = data - np.mean(data, axis=0)
    cov = np.cov(data, rowvar=False)
    # Ensure cov is 2D and valid
    if cov.ndim < 2:
        return np.zeros((data.shape[0], n_components))
    evals, evecs = np.linalg.eigh(cov)
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    return np.dot(data, evecs[:, :n_components])

def generate_figure_4(output_dir: str = "D:/drive/outputs/oglo-8figs/f004"):
    """
    Generates Figure 4: Population State-Space Dynamics (PCA) using real data.
    """
    log.progress(f"""[action] Generating Figure 4: Population State-Space in {output_dir}...""")
    
    loader = DataLoader()
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"""[action] Processing Area: {area} for PCA Manifold""")
        
        spk_aaab_list = loader.get_signal(mode="spk", condition="AAAB", area=area)
        spk_axab_list = loader.get_signal(mode="spk", condition="AXAB", area=area)
        
        if not spk_aaab_list or not spk_axab_list:
            continue
            
        psths_aaab = [np.mean(arr, axis=0) for arr in spk_aaab_list if arr.size > 0]
        psths_axab = [np.mean(arr, axis=0) for arr in spk_axab_list if arr.size > 0]
        
        if not psths_aaab or not psths_axab:
            continue
            
        # Shape: (time, units)
        pop_aaab = np.vstack(psths_aaab).T
        pop_axab = np.vstack(psths_axab).T
        
        # Smooth
        window = np.ones(100)/100
        pop_aaab_smooth = np.apply_along_axis(lambda m: np.convolve(m, window, mode='same'), axis=0, arr=pop_aaab)
        pop_axab_smooth = np.apply_along_axis(lambda m: np.convolve(m, window, mode='same'), axis=0, arr=pop_axab)
        
        # Subsample time for PCA (from -500 to 2000 ms -> indices 500 to 3000)
        t_idx = slice(500, 3000, 10) # 10ms steps
        X_aaab = pop_aaab_smooth[t_idx, :]
        X_axab = pop_axab_smooth[t_idx, :]
        
        # Fit PCA on combined
        X_combined = np.vstack([X_aaab, X_axab])
        try:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=3)
            pca.fit(X_combined)
            traj_aaab = pca.transform(X_aaab)
            traj_axab = pca.transform(X_axab)
        except ImportError:
            # Fallback to custom numpy fast_pca
            traj_combined = fast_pca(X_combined, n_components=3)
            mid = X_aaab.shape[0]
            traj_aaab = traj_combined[:mid, :]
            traj_axab = traj_combined[mid:, :]
        
        plotter = OmissionPlotter(
            title=f"Figure 4: {area} Population State-Space Dynamics",
            subtitle="3D PCA Trajectories: Standard (AAAB) vs. Omission (AXAB)"
        )
        
        plotter.fig.update_layout(
            scene=dict(
                xaxis_title="PC 1", yaxis_title="PC 2", zaxis_title="PC 3"
            )
        )
        
        plotter.fig.add_trace(go.Scatter3d(
            x=traj_aaab[:, 0], y=traj_aaab[:, 1], z=traj_aaab[:, 2], mode='lines',
            line=dict(color='black', width=4, dash='dash'), name='Standard (AAAB)'
        ))
        
        plotter.fig.add_trace(go.Scatter3d(
            x=traj_axab[:, 0], y=traj_axab[:, 1], z=traj_axab[:, 2], mode='lines',
            line=dict(color='#9400D3', width=6), name='Omission (AXAB)'
        ))
        
        plotter.save(output_dir, f"fig4_population_manifold_{area}")
        
    log.progress(f"""[action] Figure 4 complete for all areas.""")

if __name__ == "__main__":
    generate_figure_4()