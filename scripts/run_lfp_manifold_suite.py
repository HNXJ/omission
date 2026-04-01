import numpy as np
import pandas as pd
import h5py
import os
import re
import glob
import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from scipy.ndimage import gaussian_filter1d
from scipy.signal import hilbert

# Constants
BIN_MS = 100
SIGMA_MS = 100
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
WHITE = '#FFFFFF'

def get_lfp_envelope(data):
    analytical_signal = hilbert(data, axis=1)
    return np.abs(analytical_signal)

def bin_and_smooth(data, bin_ms=100, sigma_ms=100):
    # data: (Trials, Time) -> (Bins)
    n_time = data.shape[1]
    n_bins = n_time // bin_ms
    binned = data[:, :n_bins*bin_ms].reshape(-1, n_bins, bin_ms).mean(axis=2)
    smoothed = gaussian_filter1d(binned, sigma=sigma_ms/bin_ms, axis=1)
    return smoothed.mean(axis=0) # Return average across trials

def run_lfp_manifold_suite():
    data_dir = r"D:\Analysis\Omission\local-workspace\data"
    checkpoint_dir = r"D:\Analysis\Omission\local-workspace\checkpoints"
    out_dir = r"D:\Analysis\Omission\local-workspace\figures\lfp_manifolds"
    os.makedirs(out_dir, exist_ok=True)
    
    # Load metadata
    cat_df = pd.read_csv(os.path.join(checkpoint_dir, 'enhanced_lfp_categories.csv'))
    vflip_df = pd.read_csv(os.path.join(checkpoint_dir, 'vflip2_mapping_v3.csv'))
    
    sessions = cat_df['session'].unique()
    all_summary = []
    
    for ses in sessions:
        print(f"--- LFP Manifolds: Session {ses} ---")
        ses_lfp_meta = cat_df[cat_df['session'] == ses]
        
        # Load Area/Layer Mapping for this session
        ses_vflip = vflip_df[vflip_df['session_id'] == int(ses)]
        
        # Discover LFP files
        conds = ['AAAB', 'BBBA']
        lfp_data = {}
        for c in conds:
            files = glob.glob(f'{data_dir}/ses{ses}-probe*-lfp-{c}.npy')
            for f in files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                if c not in lfp_data: lfp_data[c] = {}
                lfp_data[c][p_id] = np.load(f, mmap_mode='r')
        
        if 'AAAB' not in lfp_data: continue
        
        # Map channels to Areas and Layers
        # We need a way to know which channel belongs to which area.
        # The vflip_df has 'area' column which might contain multiple areas like "V1,V2".
        
        for p_id in lfp_data['AAAB'].keys():
            # Get vflip entry for this probe
            p_meta = ses_vflip[ses_vflip['probe_id'] == p_id]
            if p_meta.empty: continue
            
            areas_str = str(p_meta.iloc[0]['area'])
            areas = [a.strip() for a in areas_str.replace('/', ',').split(',')]
            crossover = p_meta.iloc[0]['crossover']
            
            # Divide channels among areas (simple split for now)
            n_chans = lfp_data['AAAB'][p_id].shape[1]
            chans_per_area = n_chans // len(areas)
            
            for a_idx, area in enumerate(areas):
                # Filter channels for this area
                start_ch = a_idx * chans_per_area
                end_ch = (a_idx + 1) * chans_per_area
                
                # Further filter by sensitivity if desired, but here we group by Area
                area_chans = range(start_ch, end_ch)
                
                if len(area_chans) < 5: continue
                
                # Extract and process population activity
                pooled_data = []
                traj_data = {}
                for c in conds:
                    if p_id not in lfp_data[c]: continue
                    c_ch_data = []
                    for ch in area_chans:
                        env = get_lfp_envelope(lfp_data[c][p_id][:, ch, :])
                        smooth_trace = bin_and_smooth(env)
                        c_ch_data.append(smooth_trace)
                    
                    if c_ch_data:
                        c_ch_data = np.array(c_ch_data)
                        traj_data[c] = c_ch_data
                        pooled_data.append(c_ch_data)
                
                if not pooled_data: continue
                X = np.concatenate(pooled_data, axis=1).T # (Time*Cond, Channels)
                n_bins = traj_data['AAAB'].shape[1]
                
                # Algorithms
                pca = PCA(n_components=3)
                X_pca = pca.fit_transform(X)
                ev = pca.explained_variance_ratio_ * 100
                
                # UMAP
                umap_model = umap.UMAP(n_components=3, random_state=42)
                X_umap = umap_model.fit_transform(X)
                
                all_summary.append({
                    'session': ses, 'area': area, 'probe': p_id,
                    'n_chans': X.shape[1], 'ev1': ev[0], 'ev2': ev[1], 'ev3': ev[2]
                })
                
                # Plot PCA Trajectory
                fig = go.Figure()
                time_ms = np.arange(n_bins) * BIN_MS - 1000
                
                for i, c in enumerate(conds):
                    c_pca = X_pca[i*n_bins : (i+1)*n_bins]
                    fig.add_trace(go.Scatter3d(
                        x=c_pca[:, 0], y=c_pca[:, 1], z=c_pca[:, 2],
                        mode='lines+markers',
                        line=dict(color=GOLD if 'A' in c else VIOLET, width=5),
                        name=c
                    ))
                    # Add Markers
                    for p_idx, p_name in enumerate(['p1', 'p2', 'p3', 'p4']):
                        b_idx = (1000 + p_idx*1031) // BIN_MS
                        if b_idx < len(c_pca):
                            fig.add_trace(go.Scatter3d(
                                x=[c_pca[b_idx, 0]], y=[c_pca[b_idx, 1]], z=[c_pca[b_idx, 2]],
                                mode='markers+text', text=[p_name],
                                marker=dict(size=8, color='white'), showlegend=False
                            ))

                fig.update_layout(template='plotly_dark', title=f"LFP Manifold (PCA): {ses} - {area}<br>PC1-3: {sum(ev):.1f}% Var",
                                  scene=dict(xaxis_title='PC1', yaxis_title='PC2', zaxis_title='PC3'),
                                  paper_bgcolor=BLACK, plot_bgcolor=BLACK)
                fig.write_html(os.path.join(out_dir, f"LFP_TRAJ_{ses}_{area}_probe{p_id}_PCA.html"))

    pd.DataFrame(all_summary).to_csv(os.path.join(checkpoint_dir, 'lfp_manifold_summary.csv'), index=False)
    print("LFP Manifold Analysis Complete.")

if __name__ == '__main__':
    run_lfp_manifold_suite()
