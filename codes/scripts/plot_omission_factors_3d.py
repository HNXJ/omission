
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA
import umap
import os

def plot_3d_factors():
    df = pd.read_csv('checkpoints/omission_neurons_r_factors.csv')
    
    # Filter for numeric features (48 factors)
    features = df.filter(regex='_mean_|_std_')
    # Standardize
    features_norm = (features - features.mean()) / (features.std() + 1e-9)
    # Fill NaNs (if any)
    features_norm = features_norm.fillna(0)

    # 1. PCA 3D
    print("Running PCA...")
    pca = PCA(n_components=3)
    pca_results = pca.fit_transform(features_norm)
    df['pca_1'] = pca_results[:, 0]
    df['pca_2'] = pca_results[:, 1]
    df['pca_3'] = pca_results[:, 2]

    # 2. UMAP 3D
    print("Running UMAP...")
    reducer = umap.UMAP(n_components=3, random_state=42)
    umap_results = reducer.fit_transform(features_norm)
    df['umap_1'] = umap_results[:, 0]
    df['umap_2'] = umap_results[:, 1]
    df['umap_3'] = umap_results[:, 2]

    os.makedirs('figures/final_reports', exist_ok=True)

    # Plots
    for algo in ['pca', 'umap']:
        # By Area
        fig_area = px.scatter_3d(df, x=f'{algo}_1', y=f'{algo}_2', z=f'{algo}_3',
                                color='area', hover_data=['session', 'layer'],
                                title=f"Omission Neuron Manifold ({algo.upper()}) - Color by Area")
        fig_area.write_html(f"figures/final_reports/omission_neurons_{algo}_3d_area.html")
        
        # By Layer
        fig_layer = px.scatter_3d(df, x=f'{algo}_1', y=f'{algo}_2', z=f'{algo}_3',
                                 color='layer', hover_data=['session', 'area'],
                                 title=f"Omission Neuron Manifold ({algo.upper()}) - Color by Layer")
        fig_layer.write_html(f"figures/final_reports/omission_neurons_{algo}_3d_layer.html")

    print("Saved 3D Manifold plots to figures/final_reports/")

if __name__ == '__main__':
    plot_3d_factors()
