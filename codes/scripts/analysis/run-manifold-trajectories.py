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
BIN_MS = 50
SIGMA_MS = 100
WINDOWS = {
    'fx': (500, 1000),
    'p1': (1000, 1531), 'd1': (1531, 2031),
    'p2': (2031, 2562), 'd2': (2562, 3062),
    'p3': (3062, 3593), 'd3': (3593, 4093),
    'p4': (4093, 4624), 'd4': (4624, 5124)
}

GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
WHITE = '#FFFFFF'

def bin_and_smooth(data, bin_ms=50, sigma_ms=100):
    """Bins and smooths spike data (Trials, Units, Time)."""
    n_trials, n_units, n_time = data.shape
    n_bins = n_time // bin_ms
    binned = data[:, :, :n_bins*bin_ms].reshape(n_trials, n_units, n_bins, bin_ms).mean(axis=3) * 1000
    # Smooth across time
    smoothed = gaussian_filter1d(binned, sigma=sigma_ms/bin_ms, axis=2)
    return smoothed

def run_manifold_analysis():
    data_dir = r"D:\Analysis\Omission\local-workspace\data"
    checkpoint_dir = r"D:\Analysis\Omission\local-workspace\checkpoints"
    out_dir = r"D:\Analysis\Omission\local-workspace\figures\manifolds"
    os.makedirs(out_dir, exist_ok=True)
    
    # Load metadata
    cat_df = pd.read_csv(os.path.join(checkpoint_dir, 'enhanced_neuron_categories.csv'))
    vflip_df = pd.read_csv(os.path.join(checkpoint_dir, 'vflip2_mapping_v3.csv'))
    
    # Identify sessions and areas
    sessions = cat_df['session'].unique()
    
    results = []
    
    for ses in sessions:
        print(f"Analyzing Manifolds for Session {ses}...")
        ses_units = cat_df[cat_df['session'] == ses]
        
        # Load data for conditions
        conds = ['AAAB', 'BBBA', 'AXAB', 'BXBA']
        spk_data = {}
        for c in conds:
            files = glob.glob(f'{data_dir}/ses{ses}-units-probe*-spk-{c}.npy')
            for f in files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                if c not in spk_data: spk_data[c] = {}
                spk_data[c][p_id] = np.load(f, mmap_mode='r')
        
        if 'AAAB' not in spk_data: continue
        
        # Group by Area
        areas = ses_units['area'].unique()
        for area in areas:
            if pd.isna(area) or area == 'unknown': continue
            
            # Get units for this area
            area_units = ses_units[ses_units['area'] == area]
            if len(area_units) < 5: continue # Need enough units for manifold
            
            # Extract and pool data for manifold
            # Shape: (Units, TimeBins * Conditions)
            pooled_data = []
            traj_data = {}
            
            for c in ['AAAB', 'BBBA']:
                if c not in spk_data: continue
                # We need to collect all units across probes if they belong to the same area
                c_data = []
                for _, row in area_units.iterrows():
                    p = row['probe']
                    u = row['unit_idx']
                    if p in spk_data[c]:
                        unit_trace = spk_data[c][p][:, u, :] # (Trials, Time)
                        mean_trace = bin_and_smooth(unit_trace[:, np.newaxis, :], BIN_MS, SIGMA_MS)[0, 0, :]
                        c_data.append(mean_trace)
                
                if not c_data: continue
                c_data = np.array(c_data) # (N_units, N_bins)
                traj_data[c] = c_data
                pooled_data.append(c_data)
            
            if not pooled_data: continue
            X = np.concatenate(pooled_data, axis=1).T # (TimePoints, Units)
            
            # 1. PCA and Explained Variance
            pca = PCA(n_components=min(10, X.shape[1]))
            X_pca = pca.fit_transform(X)
            exp_var = pca.explained_variance_ratio_ * 100
            
            results.append({
                'session': ses,
                'area': area,
                'n_units': X.shape[1],
                'exp_var_pc1': exp_var[0],
                'exp_var_pc2': exp_var[1],
                'exp_var_pc3': exp_var[2] if len(exp_var) > 2 else 0
            })
            
            # 2. Plot Trajectory (AAAB vs BBBA)
            fig = go.Figure()
            n_bins = traj_data['AAAB'].shape[1]
            
            for i, c in enumerate(['AAAB', 'BBBA']):
                if c not in traj_data: continue
                # Project back to PCA space
                c_pca = X_pca[i*n_bins : (i+1)*n_bins]
                
                fig.add_trace(go.Scatter3d(
                    x=c_pca[:, 0], y=c_pca[:, 1], z=c_pca[:, 2] if c_pca.shape[1] > 2 else np.zeros(n_bins),
                    mode='lines+markers',
                    line=dict(color=GOLD if 'A' in c else VIOLET, width=4),
                    marker=dict(size=3, opacity=0.8),
                    name=c
                ))
                
                # Add Start/End labels
                fig.add_trace(go.Scatter3d(
                    x=[c_pca[0, 0]], y=[c_pca[0, 1]], z=[c_pca[0, 2]] if c_pca.shape[1] > 2 else [0],
                    mode='markers+text', text=[f"{c} Start"],
                    marker=dict(size=8, color='white'),
                    showlegend=False
                ))

            fig.update_layout(
                template='plotly_dark',
                title=f"Population Trajectory: {ses} - {area} (PCA)<br>N={X.shape[1]} Units | PC1+2+3: {sum(exp_var[:3]):.1f}% Var",
                scene=dict(xaxis_title='PC 1', yaxis_title='PC 2', zaxis_title='PC 3'),
                paper_bgcolor=BLACK, plot_bgcolor=BLACK
            )
            
            fig.write_html(os.path.join(out_dir, f"TRAJ_{ses}_{area}_PCA.html"))
            
    # Save Summary
    summary_df = pd.DataFrame(results)
    summary_df.to_csv(os.path.join(checkpoint_dir, 'manifold_summary.csv'), index=False)
    print("Manifold analysis complete.")

if __name__ == '__main__':
    run_manifold_analysis()
