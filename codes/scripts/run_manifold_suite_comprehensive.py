import numpy as np
import pandas as pd
import glob
import os
import re
import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from scipy.ndimage import gaussian_filter1d

# Constants
BIN_MS = 100 # Increased bin size for smoother UMAP/tSNE
SIGMA_MS = 100
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
WHITE = '#FFFFFF'

def bin_and_smooth(data, bin_ms=100, sigma_ms=100):
    """Bins and smooths spike data (Trials, Units, Time)."""
    n_trials, n_units, n_time = data.shape
    n_bins = n_time // bin_ms
    binned = data[:, :, :n_bins*bin_ms].reshape(n_trials, n_units, n_bins, bin_ms).mean(axis=3) * 1000
    smoothed = gaussian_filter1d(binned, sigma=sigma_ms/bin_ms, axis=2)
    return smoothed

def run_manifold_suite():
    data_dir = r"D:\Analysis\Omission\local-workspace\data"
    checkpoint_dir = r"D:\Analysis\Omission\local-workspace\checkpoints"
    out_dir = r"D:\Analysis\Omission\local-workspace\figures\manifolds_comprehensive"
    os.makedirs(out_dir, exist_ok=True)
    
    # Load metadata
    cat_df = pd.read_csv(os.path.join(checkpoint_dir, 'enhanced_neuron_categories.csv'))
    vflip_df = pd.read_csv(os.path.join(checkpoint_dir, 'vflip2_mapping_v3.csv'))
    
    sessions = cat_df['session'].unique()
    
    all_summary = []
    
    for ses in sessions:
        print(f"--- Comprehensive Manifolds: Session {ses} ---")
        ses_units = cat_df[cat_df['session'] == ses]
        
        # Load data
        conds = ['AAAB', 'BBBA']
        spk_data = {}
        for c in conds:
            files = glob.glob(f'{data_dir}/ses{ses}-units-probe*-spk-{c}.npy')
            for f in files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                if c not in spk_data: spk_data[c] = {}
                spk_data[c][p_id] = np.load(f, mmap_mode='r')
        
        if 'AAAB' not in spk_data: continue
        
        # We will iterate through groupings: Area, Category, Layer (if available)
        groupings = {
            'area': ses_units['area'].unique(),
            'category': ['Stim-Selective', 'Stim-Agnostic', 'Omit-Pref', 'Eye-Corr']
        }
        
        for g_type, g_list in groupings.items():
            for g_val in g_list:
                if pd.isna(g_val) or g_val == 'unknown': continue
                
                # Filter units
                if g_type == 'area':
                    mask = ses_units['area'] == g_val
                else:
                    mask = ses_units['category'].str.contains(g_val, na=False)
                
                group_units = ses_units[mask]
                if len(group_units) < 10: continue
                
                # Extract population activity
                pooled_data = []
                traj_data = {}
                for c in conds:
                    c_data = []
                    for _, row in group_units.iterrows():
                        p, u = row['probe'], row['unit_idx']
                        if p in spk_data[c]:
                            unit_trace = spk_data[c][p][:, u, :]
                            mean_trace = bin_and_smooth(unit_trace[:, np.newaxis, :])[0, 0, :]
                            c_data.append(mean_trace)
                    if c_data:
                        c_data = np.array(c_data)
                        traj_data[c] = c_data
                        pooled_data.append(c_data)
                
                if not pooled_data: continue
                X = np.concatenate(pooled_data, axis=1).T # (Time*Cond, Units)
                n_bins = traj_data['AAAB'].shape[1]
                
                # Algorithms: PCA, UMAP
                methods = {
                    'PCA': PCA(n_components=3),
                    'UMAP': umap.UMAP(n_components=3, random_state=42, n_neighbors=10)
                }
                
                for m_name, model in methods.items():
                    print(f"Running {m_name} for {g_type}={g_val}...")
                    try:
                        emb = model.fit_transform(X)
                        
                        # Summary Stats
                        if m_name == 'PCA':
                            ev = model.explained_variance_ratio_ * 100
                            all_summary.append({
                                'session': ses, 'group_type': g_type, 'group_val': g_val,
                                'n_units': X.shape[1], 'ev1': ev[0], 'ev2': ev[1], 'ev3': ev[2]
                            })
                        
                        # Plot Trajectory
                        fig = go.Figure()
                        time_ms = np.arange(n_bins) * BIN_MS - 1000
                        
                        for i, c in enumerate(conds):
                            c_emb = emb[i*n_bins : (i+1)*n_bins]
                            fig.add_trace(go.Scatter3d(
                                x=c_emb[:, 0], y=c_emb[:, 1], z=c_emb[:, 2],
                                mode='lines+markers',
                                line=dict(color=GOLD if 'A' in c else VIOLET, width=5),
                                marker=dict(size=4, opacity=0.7),
                                name=c,
                                text=[f"{t}ms" for t in time_ms]
                            ))
                            # Add Key Points (p1, p2, p3, p4 onsets)
                            for p_idx, p_name in enumerate(['p1', 'p2', 'p3', 'p4']):
                                t_val = 1000 + (p_idx * 1031) # Approx onset
                                b_idx = t_val // BIN_MS
                                if b_idx < len(c_emb):
                                    fig.add_trace(go.Scatter3d(
                                        x=[c_emb[b_idx, 0]], y=[c_emb[b_idx, 1]], z=[c_emb[b_idx, 2]],
                                        mode='markers+text', text=[p_name],
                                        marker=dict(size=10, color='white', symbol='diamond'),
                                        showlegend=False
                                    ))

                        fig.update_layout(
                            template='plotly_dark',
                            title=f"Neural Manifold ({m_name}): {ses} | {g_type}: {g_val}<br>N={X.shape[1]} Units",
                            scene=dict(xaxis_title=f'{m_name} 1', yaxis_title=f'{m_name} 2', zaxis_title=f'{m_name} 3'),
                            paper_bgcolor=BLACK, plot_bgcolor=BLACK
                        )
                        fig.write_html(os.path.join(out_dir, f"MANIFOLD_{ses}_{g_type}_{g_val}_{m_name}.html"))
                    except Exception as e:
                        print(f"Error in {m_name} for {g_val}: {e}")

    pd.DataFrame(all_summary).to_csv(os.path.join(checkpoint_dir, 'manifold_explained_variance.csv'), index=False)
    print("Comprehensive Manifold Suite Complete.")

if __name__ == '__main__':
    run_manifold_suite()
