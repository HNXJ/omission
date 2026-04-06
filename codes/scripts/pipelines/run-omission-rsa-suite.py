
import numpy as np
import pandas as pd
import os
import glob
import scipy.spatial.distance as dist
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 🏺 Madelane Golden Dark Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"

# Gamma-Standard timings: p1=1000, d1=1531, p2=2031, d2=2562, p3=3062, d3=3593, p4=4093, d4=4624
OMISSION_WINDOWS = {
    'AXAB': (2031, 2562), 'BXBA': (2031, 2562), 'RXRR': (2031, 2562),
    'AAXB': (3062, 3593), 'BBXA': (3062, 3593), 'RRXR': (3062, 3593),
    'AAAX': (4093, 4624), 'BBBX': (4093, 4624), 'RRRX': (4093, 4624)
}

AREAS = ['V1', 'V2', 'V3', 'V4', 'MT', 'MST', 'TEO', 'FST', 'DP', 'FEF', 'PFC']
BANDS = {'Theta': (4, 8), 'Alpha': (8, 13), 'Beta': (15, 25), 'Gamma': (35, 70)}

def compute_rdm(features, metric='correlation'):
    """
    Computes a Representational Dissimilarity Matrix.
    features: (n_conditions, n_features)
    """
    if features.ndim == 1:
        features = features.reshape(-1, 1)
    dists = dist.pdist(features, metric=metric)
    return dist.squareform(dists)

def linear_cka(X, Y):
    """
    Linear Centered Kernel Alignment (CKA).
    X, Y: Representational Dissimilarity Matrices (or feature matrices).
    If RDMs provided, we use them as kernels.
    """
    # Centering matrix
    n = X.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    
    # Center the kernels (RDMs act as similarity kernels here if we invert them or use them directly)
    # Standard CKA uses K = X X^T. 
    # If we have RDMs, let's treat them as distance matrices and convert to similarity
    # Or better: if X, Y are feature matrices (N x F), compute K = XX^T
    K = X @ X.T
    L = Y @ Y.T
    
    Kc = H @ K @ H
    Lc = H @ L @ H
    
    hsic = np.sum(Kc * Lc)
    norm = np.sqrt(np.sum(Kc * Kc) * np.sum(Lc * Lc))
    return hsic / (norm + 1e-12)

def run_omission_rsa():
    data_dir = r'D:\Analysis\Omission\local-workspace\data'
    checkpoint_dir = r'D:\Analysis\Omission\local-workspace\data\checkpoints'
    output_dir = r'D:\Analysis\Omission\local-workspace\figures\part01'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load mappings
    neuron_df = pd.read_csv(os.path.join(checkpoint_dir, 'enhanced_neuron_categories.csv'))
    lfp_df = pd.read_csv(os.path.join(checkpoint_dir, 'enhanced_lfp_categories.csv'))
    
    sessions = ['230630', '230816', '230818', '230823', '230825', '230830']
    
    # Conditions to compare (The "Representational Space")
    # We want to see how the system represents different omission types
    CONDITIONS = ['AXAB', 'AAXB', 'AAAX', 'BXBA', 'BBXA', 'BBBX', 'RXRR', 'RRXR', 'RRRX']
    
    all_rdms = {} # (area, modality) -> RDM
    
    for sid in sessions:
        print(f"🏺 RSA Suite: Session {sid}")
        
        for area in AREAS:
            # 1. Spiking Features
            area_units = neuron_df[(neuron_df['session_id'].astype(str).str.contains(sid)) & (neuron_df['area'] == area)]
            if len(area_units) < 5: continue
            
            spike_features = []
            valid_conds = []
            
            for cond in CONDITIONS:
                probes = area_units['probe'].unique()
                cond_vec = []
                win = OMISSION_WINDOWS.get(cond, (4093, 4624)) # Default to P4
                
                for p in probes:
                    f = os.path.join(data_dir, f'ses{sid}-units-probe{p}-spk-{cond}.npy')
                    if os.path.exists(f):
                        try:
                            spikes = np.nan_to_num(np.load(f, mmap_mode='r'))
                            # mean rate in condition-specific window
                            mean_rate = np.mean(spikes[:, :, win[0]:win[1]], axis=(0, 2))
                            cond_vec.extend(mean_rate)
                        except Exception: continue
                
                if cond_vec:
                    spike_features.append(cond_vec)
                    valid_conds.append(cond)
            
            if len(spike_features) > 3:
                all_rdms[(area, sid, 'Spikes')] = {
                    'rdm': compute_rdm(np.array(spike_features)),
                    'conds': valid_conds,
                    'features': np.array(spike_features)
                }

            # 2. LFP Features (Power in bands)
            area_probes = lfp_df[(lfp_df['session_id'].astype(str).str.contains(sid)) & (lfp_df['area'] == area)]
            if area_probes.empty: continue
            
            lfp_features = []
            
            for cond in valid_conds: # Use same conditions for LFP-Spike RSA
                cond_vec = []
                for _, row in area_probes.iterrows():
                    p = row['probe_id']
                    f = os.path.join(data_dir, f'ses{sid}-probe{p}-lfp-{cond}.npy')
                    if os.path.exists(f):
                        lfp = np.load(f, mmap_mode='r') # (trials, channels, time)
                        # Compute power in bands for omission window
                        # Sample 1000 is onset. Window is 4093-4624 (Sample 1000=0ms)
                        # So OMIT_WINDOW (3093, 3624) relative to P1 onset.
                        win_data = lfp[:, :, 1000+OMIT_WINDOW[0]:1000+OMIT_WINDOW[1]]
                        
                        # Mean across trials and channels, then across time? 
                        # Or better: mean power per band
                        # Using simple variance as power proxy for speed or proper FFT?
                        # Let's use Variance of filtered signal or just Variance of signal as "broadband"
                        # Or pre-extracted power if available. 
                        # For RSA, we'll use mean power in the 4 bands per channel.
                        # (trials, channels, time) -> (channels, bands)
                        chan_means = []
                        for ch in range(win_data.shape[1]):
                            # Just use variance for now as broad power proxy
                            chan_means.append(np.var(win_data[:, ch, :]))
                        cond_vec.extend(chan_means)
                
                if cond_vec:
                    lfp_features.append(cond_vec)
            
            if len(lfp_features) == len(spike_features):
                all_rdms[(area, sid, 'LFP')] = {
                    'rdm': compute_rdm(np.array(lfp_features)),
                    'conds': valid_conds,
                    'features': np.array(lfp_features)
                }

    # --- Cross-Modality & Cross-Area Comparison ---
    rsa_results = []
    
    # 1. LFP vs Spikes RSA per area
    for (area, sid, mod), data in all_rdms.items():
        if mod == 'Spikes' and (area, sid, 'LFP') in all_rdms:
            lfp_data = all_rdms[(area, sid, 'LFP')]
            # Compare feature matrices using CKA
            cka = linear_cka(data['features'], lfp_data['features'])
            rsa_results.append({
                'type': 'LFP_vs_Spikes',
                'area': area,
                'session': sid,
                'score': cka
            })

    # 2. Area vs Area RSA (Spikes)
    for sid in sessions:
        areas_in_sid = [a for (a, s, m) in all_rdms.keys() if s == sid and m == 'Spikes']
        for i, a1 in enumerate(areas_in_sid):
            for a2 in areas_in_sid[i+1:]:
                cka = linear_cka(all_rdms[(a1, sid, 'Spikes')]['features'], 
                                all_rdms[(a2, sid, 'Spikes')]['features'])
                rsa_results.append({
                    'type': 'Area_vs_Area',
                    'area': f"{a1}-{a2}",
                    'session': sid,
                    'score': cka
                })

    # Save and Plot
    df_rsa = pd.DataFrame(rsa_results)
    df_rsa.to_csv(os.path.join(checkpoint_dir, 'omission_rsa_cka_summary.csv'), index=False)
    
    # Visualization
    fig = go.Figure()
    # Average across sessions
    summary = df_rsa.groupby(['type', 'area'])['score'].mean().reset_index()
    
    for rsa_type in summary['type'].unique():
        sub = summary[summary['type'] == rsa_type]
        fig.add_trace(go.Bar(x=sub['area'], y=sub['score'], name=rsa_type))
        
    fig.update_layout(title="🏺 Representational Similarity (CKA)", 
                      template="plotly_white")
    fig.write_html(os.path.join(output_dir, "FIG_10_RSA_CKA_Hierarchy.html"))
    print("RSA Suite Complete.")

if __name__ == '__main__':
    run_omission_rsa()
