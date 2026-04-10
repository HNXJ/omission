
import numpy as np
import pandas as pd
from pathlib import Path
import re
from sklearn.decomposition import PCA
import plotly.graph_objects as go

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\unit_nwb_profile.csv')
AUDIT_PATH = Path(r'D:\drive\omission\outputs\unit_refined_categories_v2.csv')
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_ses(s):
    match = re.search(r'ses-(\d+)', str(s))
    return match.group(1) if match else None

def map_area(row):
    loc = str(row['location'])
    ch_local = row['peak_channel_id'] % 128
    if ',' in loc:
        parts = [p.strip() for p in loc.split(',')]
        if len(parts) == 2: return parts[0] if ch_local < 64 else parts[1]
        elif len(parts) == 3:
            if ch_local < 42: return parts[0]
            elif ch_local < 84: return parts[1]
            else: return parts[2]
    return 'V4' if loc == 'DP' else loc

def generate_figure_5():
    # Load and prep
    df = pd.read_csv(PROFILE_PATH, low_memory=False)
    full_audit = pd.read_csv(AUDIT_PATH)
    
    df['ses_tmp'] = df['session_nwb'].apply(extract_ses)
    df['refined_key'] = df['ses_tmp'] + "_" + df['unit_id_in_session'].astype(str)
    full_audit['refined_key'] = full_audit['session_id'].astype(str) + "_" + full_audit['unit_id'].astype(str)
    
    df = pd.merge(df, full_audit[['refined_key', 'is_stable_ultimate']], on='refined_key', how='left')
    df['area_hier'] = df.apply(map_area, axis=1)
    
    df['probe_id'] = df['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df['local_idx'] = df.groupby(['session_nwb', 'probe_id']).cumcount()

    CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    df_stable = df[(df['is_stable_ultimate'] == True) & df['area_hier'].isin(CANONICAL_AREAS)].copy()
    
    unique_sessions = df_stable['ses_tmp'].dropna().unique()
    
    # 2562 ms total time, 250ms window, 50ms step => 47 bins
    window_size = 250
    step_size = 50
    n_bins = (2562 - window_size) // step_size + 1
    
    area_g1 = {area: [] for area in CANONICAL_AREAS}
    area_g2 = {area: [] for area in CANONICAL_AREAS}
    
    for session in unique_sessions:
        for probe in [0, 1, 2]:
            units = df_stable[(df_stable['ses_tmp'] == session) & (df_stable['probe_id'] == probe)]
            if units.empty: continue
            
            path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
            if not path.exists(): continue
            
            data = np.load(path) # (trials, units, time)
            data_mean = data.mean(axis=0) # average across exact same trials
            
            for _, row in units.iterrows():
                l_idx = row['local_idx']
                if l_idx >= data_mean.shape[0]: continue
                
                # Group 1: 2562 to 5124 (d2-p3-d3-p4-d4)
                g1_raw = data_mean[l_idx, 2562:5124]
                # Group 2: 1531 to 4093 (d1-p2-d2-p3-d3)
                g2_raw = data_mean[l_idx, 1531:4093]
                
                g1_bins, g2_bins = [], []
                for b in range(n_bins):
                    start = b * step_size
                    end = start + window_size
                    # Sum and convert to Hz
                    g1_bins.append(g1_raw[start:end].sum() * (1000.0 / window_size))
                    g2_bins.append(g2_raw[start:end].sum() * (1000.0 / window_size))
                    
                area_g1[row['area_hier']].append(g1_bins)
                area_g2[row['area_hier']].append(g2_bins)

    fig = go.Figure()

    for area in CANONICAL_AREAS:
        if len(area_g1[area]) < 3: continue
            
        G1 = np.array(area_g1[area]).T # (47, N_neurons)
        G2 = np.array(area_g2[area]).T
        
        # Soft-standardization across neurons
        X = np.vstack([G1, G2])
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-6)
        
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X)
        
        G1_pca = X_pca[:n_bins]
        G2_pca = X_pca[n_bins:]
        
        # Center them to start around the same space for cross-area comparison
        start_mean = (G1_pca[0] + G2_pca[0]) / 2
        G1_pca -= start_mean
        G2_pca -= start_mean
        
        # We can add an endpoint marker to show direction clearly
        fig.add_trace(go.Scatter3d(
            x=G1_pca[:,0], y=G1_pca[:,1], z=G1_pca[:,2],
            mode='lines',
            line=dict(color='royalblue', width=4),
            name=f'{area} Standard',
            showlegend=False,
            hovertext=[f'{area} Standard t={b*50}ms' for b in range(n_bins)],
            hoverinfo='text'
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[G1_pca[-1,0]], y=[G1_pca[-1,1]], z=[G1_pca[-1,2]],
            mode='markers', marker=dict(size=4, color='royalblue', symbol='diamond'),
            showlegend=False, hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter3d(
            x=G2_pca[:,0], y=G2_pca[:,1], z=G2_pca[:,2],
            mode='lines',
            line=dict(color='crimson', width=4),
            name=f'{area} Omission',
            showlegend=False,
            hovertext=[f'{area} Omission t={b*50}ms' for b in range(n_bins)],
            hoverinfo='text'
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[G2_pca[-1,0]], y=[G2_pca[-1,1]], z=[G2_pca[-1,2]],
            mode='markers', marker=dict(size=4, color='crimson', symbol='diamond'),
            showlegend=False, hoverinfo='skip'
        ))

    # Proxy legends
    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines+markers', line=dict(color='royalblue', width=6), marker=dict(color='royalblue', symbol='diamond'), name='Standard (d2-p3-d3-p4-d4)'))
    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines+markers', line=dict(color='crimson', width=6), marker=dict(color='crimson', symbol='diamond'), name='Omission (d1-p2[x]-d2-p3-d3)'))

    fig.update_layout(
        title='Figure 5: Population State-Space Dynamics (PCA Projection)<br><i>Aligned trajectories across 11 areas. Diamond marks end of trajectory.</i>',
        scene=dict(
            xaxis_title='PC 1 (Variance)',
            yaxis_title='PC 2 (Variance)',
            zaxis_title='PC 3 (Variance)',
            bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='gray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='gray'),
            zaxis=dict(showgrid=True, gridcolor='lightgray', zerolinecolor='gray')
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.05),
        width=1000, height=800
    )
    
    out_html = OUTPUT_DIR / 'figure_5_state_space.html'
    fig.write_html(out_html)
    print(f"Saved interactive 3D PCA plot to {out_html}")

if __name__ == "__main__":
    generate_figure_5()
