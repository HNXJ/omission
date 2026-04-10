
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
    
    window_size = 500
    step_size = 100
    n_bins = (2562 - window_size) // step_size + 1
    
    area_G1_trials = {area: [] for area in CANONICAL_AREAS}
    area_G2_trials = {area: [] for area in CANONICAL_AREAS}
    
    for session in unique_sessions:
        for probe in [0, 1, 2]:
            units = df_stable[(df_stable['ses_tmp'] == session) & (df_stable['probe_id'] == probe)]
            if units.empty: continue
            
            path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
            if not path.exists(): continue
            
            data = np.load(path) # (trials, units, time)
            n_trials = data.shape[0]
            
            for _, row in units.iterrows():
                l_idx = row['local_idx']
                if l_idx >= data.shape[1]: continue
                
                g1_raw = data[:, l_idx, 2562:5124]
                g2_raw = data[:, l_idx, 1531:4093]
                
                g1_binned = np.zeros((n_trials, n_bins))
                g2_binned = np.zeros((n_trials, n_bins))
                
                for b in range(n_bins):
                    start = b * step_size
                    end = start + window_size
                    g1_binned[:, b] = g1_raw[:, start:end].sum(axis=1) * (1000.0 / window_size)
                    g2_binned[:, b] = g2_raw[:, start:end].sum(axis=1) * (1000.0 / window_size)
                    
                area_G1_trials[row['area_hier']].append(g1_binned)
                area_G2_trials[row['area_hier']].append(g2_binned)

    fig = go.Figure()
    
    time_array = np.arange(n_bins)

    for area in CANONICAL_AREAS:
        if len(area_G1_trials[area]) < 3: continue
            
        G1_neurons = area_G1_trials[area]
        G2_neurons = area_G2_trials[area]
        
        min_t = min([x.shape[0] for x in G1_neurons])
        if min_t == 0: continue
            
        G1_trials = np.stack([x[:min_t, :] for x in G1_neurons], axis=-1) # (min_t, n_bins, N)
        G2_trials = np.stack([x[:min_t, :] for x in G2_neurons], axis=-1)
        
        G1_mean = G1_trials.mean(axis=0) # (n_bins, N)
        G2_mean = G2_trials.mean(axis=0)
        
        X_mean = np.vstack([G1_mean, G2_mean])
        scaler_mean = X_mean.mean(axis=0)
        scaler_std = X_mean.std(axis=0) + 1e-6
        
        G1_mean_sc = (G1_mean - scaler_mean) / scaler_std
        G2_mean_sc = (G2_mean - scaler_mean) / scaler_std
        
        pca = PCA(n_components=3)
        pca.fit(np.vstack([G1_mean_sc, G2_mean_sc]))
        
        G1_mean_pca = pca.transform(G1_mean_sc)
        G2_mean_pca = pca.transform(G2_mean_sc)
        
        start_mean = (G1_mean_pca[0] + G2_mean_pca[0]) / 2
        G1_mean_pca -= start_mean
        G2_mean_pca -= start_mean
        
        # Transform individual trials
        G1_trials_pca = np.zeros((min_t, n_bins, 3))
        G2_trials_pca = np.zeros((min_t, n_bins, 3))
        for t in range(min_t):
            g1_sc = (G1_trials[t] - scaler_mean) / scaler_std
            g2_sc = (G2_trials[t] - scaler_mean) / scaler_std
            G1_trials_pca[t] = pca.transform(g1_sc) - start_mean
            G2_trials_pca[t] = pca.transform(g2_sc) - start_mean

        # Plot individual trials (thin, semi-transparent)
        for t in range(min_t):
            fig.add_trace(go.Scatter3d(
                x=G1_trials_pca[t,:,0], y=G1_trials_pca[t,:,1], z=G1_trials_pca[t,:,2],
                mode='lines', line=dict(color='rgba(65, 105, 225, 0.15)', width=2),
                showlegend=False, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter3d(
                x=G2_trials_pca[t,:,0], y=G2_trials_pca[t,:,1], z=G2_trials_pca[t,:,2],
                mode='lines', line=dict(color='rgba(220, 20, 60, 0.15)', width=2),
                showlegend=False, hoverinfo='skip'
            ))
            
        # Plot mean trajectories (thick, colored by time)
        fig.add_trace(go.Scatter3d(
            x=G1_mean_pca[:,0], y=G1_mean_pca[:,1], z=G1_mean_pca[:,2],
            mode='lines+markers',
            line=dict(color=time_array, colorscale='Blues', width=8),
            marker=dict(size=4, color=time_array, colorscale='Blues'),
            name=f'{area} Standard Mean',
            showlegend=False,
            hovertext=[f'{area} Standard t={b*step_size}ms' for b in range(n_bins)],
            hoverinfo='text'
        ))
        fig.add_trace(go.Scatter3d(
            x=[G1_mean_pca[-1,0]], y=[G1_mean_pca[-1,1]], z=[G1_mean_pca[-1,2]],
            mode='markers', marker=dict(size=8, color='darkblue', symbol='diamond'),
            showlegend=False, hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter3d(
            x=G2_mean_pca[:,0], y=G2_mean_pca[:,1], z=G2_mean_pca[:,2],
            mode='lines+markers',
            line=dict(color=time_array, colorscale='Reds', width=8),
            marker=dict(size=4, color=time_array, colorscale='Reds'),
            name=f'{area} Omission Mean',
            showlegend=False,
            hovertext=[f'{area} Omission t={b*step_size}ms' for b in range(n_bins)],
            hoverinfo='text'
        ))
        fig.add_trace(go.Scatter3d(
            x=[G2_mean_pca[-1,0]], y=[G2_mean_pca[-1,1]], z=[G2_mean_pca[-1,2]],
            mode='markers', marker=dict(size=8, color='darkred', symbol='diamond'),
            showlegend=False, hoverinfo='skip'
        ))

    # Proxy legends
    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='rgba(65, 105, 225, 0.4)', width=2), name='Standard Individual Trials'))
    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='rgba(220, 20, 60, 0.4)', width=2), name='Omission Individual Trials'))
    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines+markers', line=dict(color='blue', width=8), marker=dict(color='darkblue', symbol='diamond', size=8), name='Standard Mean Trajectory (Gradient = Time)'))
    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines+markers', line=dict(color='red', width=8), marker=dict(color='darkred', symbol='diamond', size=8), name='Omission Mean Trajectory (Gradient = Time)'))

    fig.update_layout(
        title='Figure 5: Population State-Space Dynamics (PCA Projection)<br><i>Individual trials (thin) and mean trajectories (thick, colored by time) across 11 areas.</i>',
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
        width=1200, height=900
    )
    
    out_html = OUTPUT_DIR / 'figure_5_state_space.html'
    fig.write_html(out_html)
    print(f"Saved interactive 3D PCA plot to {out_html}")

if __name__ == "__main__":
    generate_figure_5()
