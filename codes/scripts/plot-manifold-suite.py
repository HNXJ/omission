
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import os

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
AREA_COLORS = {
    'V1': '#FF0000',   'V2': '#FF7F00',   'V3d': '#FFFF00',  'V3a': '#7FFF00',
    'V4': '#00FF00',   'MT': '#00FF7F',   'MST': '#00FFFF',  'TEO': '#007FFF',
    'FST': '#0000FF',  'FEF': '#7F00FF',  'PFC': '#FF00FF'
}

CATEGORY_COLORS = {
    'null': '#808080',  # Gray
    'oxm+': '#FF0000',  # Red (Omission)
    'fx+': '#0000FF',   # Blue (Fixation)
    'stim+': '#00FF00', # Green
    'stim-': '#00FFFF'  # Cyan
}

def plot_manifold_suite():
    factors_path = 'checkpoints/omission_neurons_r_factors.csv'
    if not os.path.exists(factors_path):
        print("Waiting for factors matrix...")
        return

    df = pd.read_csv(factors_path)
    print(f"Loaded {len(df)} neurons with {df.shape[1]} columns.")

    # 1. Integration with Neuron Categories
    if os.path.exists('checkpoints/neuron_categories.csv'):
        cat_df = pd.read_csv('checkpoints/neuron_categories.csv')
        df['session'] = df['session'].astype(str)
        df['probe'] = df['probe'].astype(int)
        df['unit_idx'] = df['unit_idx'].astype(int)
        cat_df['session'] = cat_df['session'].astype(str)
        cat_df['probe'] = cat_df['probe'].astype(int)
        cat_df['unit_idx'] = cat_df['unit_idx'].astype(int)
        
        if 'category' in df.columns: df = df.drop(columns=['category'])
        df = df.merge(cat_df[['session', 'probe', 'unit_idx', 'category']], 
                      on=['session', 'probe', 'unit_idx'], 
                      how='left')
    
    # Pre-processing
    features = df.filter(regex='_mean_|_std_')
    features_norm = (features - features.mean()) / (features.std() + 1e-9)
    features_norm = features_norm.fillna(0)

    os.makedirs('figures/final_reports/manifolds', exist_ok=True)

    # Algorithms
    methods = {
        'PCA': PCA(n_components=3),
        'UMAP': umap.UMAP(n_components=3, random_state=42, n_neighbors=15, min_dist=0.1),
        'tSNE': TSNE(n_components=3, random_state=42, init='pca', learning_rate='auto')
    }

    results = {}
    for name, model in methods.items():
        print(f"Running {name}...")
        results[name] = model.fit_transform(features_norm)

    # Plotting loop
    for name, emb in results.items():
        df[f'{name}_1'] = emb[:, 0]
        df[f'{name}_2'] = emb[:, 1]
        df[f'{name}_3'] = emb[:, 2]
        
        # Calculate explained variance for PCA
        extra_title = ""
        if name == 'PCA':
            var_exp = methods['PCA'].explained_variance_ratio_ * 100
            extra_title = f" (ExpVar: {var_exp[0]:.1f}%, {var_exp[1]:.1f}%, {var_exp[2]:.1f}%)"

        for color_by in ['area', 'layer', 'category']:
            if color_by not in df.columns: continue
            
            # Select color map
            if color_by == 'area':
                color_map = AREA_COLORS
            elif color_by == 'category':
                color_map = CATEGORY_COLORS
            else:
                color_map = px.colors.qualitative.Alphabet

            cat_orders = {'area': AREA_ORDER} if color_by == 'area' else None
            
            # Add counts to labels for better detail
            counts = df[color_by].value_counts()
            df_plot = df.copy()
            df_plot[f'{color_by}_with_n'] = df_plot[color_by].apply(lambda x: f"{x} (n={counts.get(x, 0)})")
            
            # Update orders and map if we changed the column name
            new_color_by = f'{color_by}_with_n'
            new_color_map = None
            if isinstance(color_map, dict):
                new_color_map = {f"{k} (n={counts.get(k, 0)})": v for k, v in color_map.items()}
            
            new_cat_orders = None
            if cat_orders:
                new_cat_orders = {new_color_by: [f"{k} (n={counts.get(k, 0)})" for k in cat_orders[color_by]]}

            # --- GENERATE V1 (Standard) ---
            fig_3d = px.scatter_3d(
                df_plot, x=f'{name}_1', y=f'{name}_2', z=f'{name}_3',
                color=new_color_by, opacity=0.5,
                color_discrete_map=new_color_map if isinstance(new_color_map, dict) else None,
                color_discrete_sequence=color_map if not isinstance(color_map, dict) else None,
                category_orders=new_cat_orders,
                title=f"Neuron Manifold ({name} 3D) - Color by {color_by.capitalize()}{extra_title}<br>Total Neurons: {len(df)}",
                template="plotly_white", height=900,
                labels={f'{name}_1': f'{name} 1', f'{name}_2': f'{name} 2', f'{name}_3': f'{name} 3'}
            )
            fig_3d.update_traces(marker=dict(size=1.5))
            fig_3d.update_layout(legend={'itemsizing': 'constant'})
            fig_3d.write_html(f"figures/final_reports/manifolds/FIG_05_{name}_3D_{color_by}.html")

            # 2D Plot
            fig_2d = px.scatter(
                df_plot, x=f'{name}_1', y=f'{name}_2',
                color=new_color_by, opacity=0.5,
                color_discrete_map=new_color_map if isinstance(new_color_map, dict) else None,
                color_discrete_sequence=color_map if not isinstance(color_map, dict) else None,
                category_orders=new_cat_orders,
                title=f"Neuron Manifold ({name} 2D) - Color by {color_by.capitalize()}{extra_title}<br>Total Neurons: {len(df)}",
                template="plotly_white", height=700,
                labels={f'{name}_1': f'{name} 1', f'{name}_2': f'{name} 2'}
            )
            fig_2d.update_traces(marker=dict(size=2.5))
            fig_2d.update_layout(legend={'itemsizing': 'constant'})
            fig_2d.write_html(f"figures/final_reports/manifolds/FIG_05_{name}_2D_{color_by}.html")

            # --- GENERATE V2 (With Centroids) ---
            fig_v2 = go.Figure(fig_3d)
            
            # Using the original 'group' for centroid calculation
            groups = df[color_by].unique()
            for group in groups:
                if pd.isna(group): continue
                mask = df[color_by] == group
                centroid = df[mask][[f'{name}_1', f'{name}_2', f'{name}_3']].mean()
                
                # Match color
                color = None
                if isinstance(color_map, dict):
                    color = color_map.get(group)
                
                if color is None:
                    # Search in figure traces
                    search_name = f"{group} (n={counts.get(group, 0)})"
                    for trace in fig_3d.data:
                        if trace.name == search_name:
                            color = trace.marker.color
                            break

                fig_v2.add_trace(go.Scatter3d(
                    x=[centroid[0]], y=[centroid[1]], z=[centroid[2]],
                    mode='markers+text',
                    marker=dict(size=15, color=color, opacity=0.8, symbol='circle'),
                    name=f"{group} Centroid",
                    text=[f"{group}"],
                    textposition="top center",
                    showlegend=True
                ))
            
            fig_v2.update_layout(title=f"Neuron Manifold ({name} 3D V2) - Centroids indicated{extra_title}<br>N={len(df)}")
            fig_v2.write_html(f"figures/final_reports/manifolds/FIG_05_{name}_3D_{color_by}_v2.html")

    print("Saved comprehensive manifold suite (Standard and V2) to figures/final_reports/manifolds/")

if __name__ == '__main__':
    plot_manifold_suite()
