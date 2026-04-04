
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA
import umap
import os

AREA_COLORS = {
    'V1': 'red', 'V2': 'orange', 'V3d': 'yellow', 'V3a': 'gold',
    'V4': 'green', 'MT': 'cyan', 'MST': 'teal', 'TEO': 'blue',
    'FST': 'darkblue', 'FEF': 'magenta', 'PFC': 'purple'
}

def get_ellipsoid(centroid, cov, color, name, n_std=1.0):
    """Generates a 3D ellipsoid trace based on centroid and covariance."""
    # Eigenvalues and eigenvectors
    vals, vecs = np.linalg.eigh(cov)
    # Radii are proportional to sqrt of eigenvalues
    radii = n_std * np.sqrt(vals)
    
    # Spherical coordinates
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x = radii[0] * np.outer(np.cos(u), np.sin(v))
    y = radii[1] * np.outer(np.sin(u), np.sin(v))
    z = radii[2] * np.outer(np.ones_like(u), np.cos(v))
    
    # Rotate ellipsoid
    for i in range(len(x)):
        for j in range(len(x)):
            [x[i,j], y[i,j], z[i,j]] = np.dot([x[i,j], y[i,j], z[i,j]], vecs.T) + centroid
            
    return go.Surface(x=x, y=y, z=z, opacity=0.15, colorscale=[[0, color], [1, color]], 
                      showscale=False, name=f"{name} Cloud", legendgroup=name)

def plot_refined_manifold():
    df = pd.read_csv('checkpoints/omission_neurons_r_factors.csv')
    features = df.filter(regex='_mean_|_std_')
    features_norm = (features - features.mean()) / (features.std() + 1e-9)
    features_norm = features_norm.fillna(0)

    # Dimensionality Reduction
    pca_results = PCA(n_components=3).fit_transform(features_norm)
    reducer = umap.UMAP(n_components=3, random_state=42)
    umap_results = reducer.fit_transform(features_norm)

    for name, results in [('PCA', pca_results), ('UMAP', umap_results)]:
        df[f'{name.lower()}_1'] = results[:, 0]
        df[f'{name.lower()}_2'] = results[:, 1]
        df[f'{name.lower()}_3'] = results[:, 2]

        fig = go.Figure()

        for area, color in AREA_COLORS.items():
            mask = df['area'] == area
            if not mask.any(): continue
            
            sub = df[mask]
            pts = results[mask]
            
            # 1. Add Scatter points
            fig.add_trace(go.Scatter3d(
                x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
                mode='markers', marker=dict(size=3, color=color, opacity=0.7),
                name=area, legendgroup=area,
                hovertext=[f"S:{s} L:{l} C:{c}" for s, l, c in zip(sub['session'], sub['layer'], sub['channel'])]
            ))
            
            # 2. Add Centroid Cloud (Ellipsoid)
            if len(pts) > 5:
                centroid = np.mean(pts, axis=0)
                cov = np.cov(pts, rowvar=False)
                fig.add_trace(get_ellipsoid(centroid, cov, color, area))

        fig.update_layout(
            title=f"Refined Omission Neuron Manifold ({name}) - Area Clouds",
            scene=dict(xaxis_title='Dim 1', yaxis_title='Dim 2', zaxis_title='Dim 3'),
            template="plotly_white", height=900
        )
        
        os.makedirs('figures/final_reports', exist_ok=True)
        fig.write_html(f"figures/final_reports/omission_neurons_{name.lower()}_3d_refined.html")
        print(f"Saved refined {name} plot.")

if __name__ == '__main__':
    plot_refined_manifold()
