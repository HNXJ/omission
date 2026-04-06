
from codes.config.paths import DATA_DIR, FIGURES_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas as pd
import os
import glob
import scipy.spatial.distance as dist
from scipy.stats import spearmanr
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 🏺 Madelane Golden Dark Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"

# Configuration
AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
SESSIONS = ['230630', '230816', '230818', '230823', '230825', '230830']
DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
OUTPUT_DIR = str(FIGURES_DIR / 'part01')

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Time Windows (Relative to P1 onset=1000)
    WINDOWS = {
    'p1': (0, 500), 'd1': (500, 1031),
    'p2': (1031, 1531), 'd2': (1531, 2062),
    'p3': (2062, 2562), 'd3': (2562, 3093),
    'p4': (3093, 3593), 'd4': (3593, 4124)
    }
    # Context Definitions
    CONTEXTS = {
    'Delay': {'windows': ['d1', 'd2', 'd3', 'd4'], 'conds': ['AAAB', 'BBBA', 'RRRR']},
    'Omission': {'windows': ['p2', 'p3', 'p4'], 'conds': ['AXAB', 'AAXB', 'AAAX', 'BXBA', 'BBXA', 'BBBX', 'RXRR', 'RRXR', 'RRRX']},
    'Stimulus': {'windows': ['p1', 'p2', 'p3', 'p4'], 'conds': ['AAAB', 'BBBA', 'RRRR']},
    'All_Time': {'windows': list(WINDOWS.keys()), 'conds': ['AAAB', 'BBBA', 'RRRR']}
    }
    def linear_cka(X, Y):
    """Linear Centered Kernel Alignment."""
    n = X.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    K = X @ X.T
    L = Y @ Y.T
    Kc = H @ K @ H
    Lc = H @ L @ H
    hsic = np.sum(Kc * Lc)
    norm = np.sqrt(np.sum(Kc * Kc) * np.sum(Lc * Lc))
    return hsic / (norm + 1e-12)
    def extract_features(sid, area, modality, context_name, neuron_df, mapping_df):
    """Extracts feature matrix [Items x Features] for a context."""
    ctx = CONTEXTS[context_name]
    feature_matrix = []
    if modality == 'Spikes':
        # Find units
        area_units = neuron_df[(neuron_df['session'].astype(str).str.contains(sid)) & (neuron_df['area'] == area)]
        if len(area_units) < 3: return None
        probes = area_units['probe'].unique()
        for cond in ctx['conds']:
            for win_name in ctx['windows']:
                win = WINDOWS[win_name]
                item_vec = []
                for p in probes:
                    f = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond}.npy')
                    if os.path.exists(f):
                        data = np.load(f, mmap_mode='r')
                        mean_rate = np.mean(data[:, :, win[0]:win[1]], axis=(0, 2))
                        item_vec.extend(mean_rate)
                if item_vec:
                    feature_matrix.append(item_vec)
    else: # LFP
        # Use mapping_df to find probes for this area
        # Note: mapping_df area might be "V1,V2"
        area_probes = mapping_df[(mapping_df['session_id'].astype(str).str.contains(sid)) & 
                                (mapping_df['area'].str.contains(area))]
        if area_probes.empty: return None
        for cond in ctx['conds']:
            for win_name in ctx['windows']:
                win = WINDOWS[win_name]
                item_vec = []
                for _, row in area_probes.iterrows():
                    p = row['probe_id']
                    f = os.path.join(DATA_DIR, f'ses{sid}-probe{p}-lfp-{cond}.npy')
                    if os.path.exists(f):
                        data = np.load(f, mmap_mode='r')
                        win_data = data[:, :, 1000+win[0]:1000+win[1]]
                        item_vec.extend(np.var(win_data, axis=(0, 2)))
                if item_vec:
                    feature_matrix.append(item_vec)
    return np.array(feature_matrix) if len(feature_matrix) > 0 else None
    def run_massive_rsa():
    neuron_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'enhanced_neuron_categories.csv'))
    mapping_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    # Store results: (Context, ModalityPair) -> 11x11 matrix
    results = {}
    modality_pairs = [('Spikes', 'Spikes'), ('LFP', 'LFP'), ('Spiking', 'LFP')]
    for ctx_name in CONTEXTS.keys():
        print(f"🏺 Processing Context: {ctx_name}")
        for m1, m2 in modality_pairs:
            cka_sum = np.zeros((11, 11))
            count_sum = np.zeros((11, 11))
            for sid in SESSIONS:
                # Extract all area features for this session once
                features = {}
                for area in AREAS:
                    f1 = extract_features(sid, area, 'Spikes' if m1=='Spiking' else m1, ctx_name, neuron_df, mapping_df)
                    f2 = extract_features(sid, area, m2, ctx_name, neuron_df, mapping_df)
                    if f1 is not None: features[(area, m1)] = f1
                    if f2 is not None: features[(area, m2)] = f2
                # Compute pairwise CKA
                for i, a1 in enumerate(AREAS):
                    for j, a2 in enumerate(AREAS):
                        if (a1, m1) in features and (a2, m2) in features:
                            # Must have same number of items (rows)
                            if features[(a1, m1)].shape[0] == features[(a2, m2)].shape[0]:
                                score = linear_cka(features[(a1, m1)], features[(a2, m2)])
                                cka_sum[i, j] += score
                                count_sum[i, j] += 1
            # Average and plot
            avg_matrix = cka_sum / (count_sum + 1e-12)
            results[(ctx_name, m1, m2)] = avg_matrix
            # Visualization
            fig = go.Figure(data=go.Heatmap(
                z=avg_matrix, x=AREAS, y=AREAS,
                colorscale=[[0, BLACK], [0.5, VIOLET], [1, GOLD]],
                zmin=0, zmax=1,
                colorbar=dict(title="CKA Similarity"),
                # Smoothing for "upsampled" look
                zsmooth='best'
            ))
            fig.update_layout(
                title=f"🏺 MASSIVE RSA | {m1} vs {m2} | {ctx_name}",
                width=800, height=800,
                paper_bgcolor=BLACK, plot_bgcolor=BLACK,
                font=dict(color=GOLD, family="Consolas"),
                xaxis=dict(tickangle=-45),
                template="plotly_dark"
            )
            # Save HTML and SVG
            base_name = f"RSA_{m1}_vs_{m2}_{ctx_name}"
            fig.write_html(os.path.join(OUTPUT_DIR, f"{base_name}.html"))
            # Note: svg requires kaleido, assuming available or falling back to warning
            try:
                fig.write_image(os.path.join(OUTPUT_DIR, f"{base_name}.svg"))
            except:
                print(f"Warning: Could not save SVG for {base_name} (Kaleido missing).")
    print("Massive RSA Hierarchy Complete.")
    run_massive_rsa()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
