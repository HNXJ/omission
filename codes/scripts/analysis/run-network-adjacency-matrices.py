
from codes.config.paths import DATA_DIR, FIGURES_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas as pd
import os
import glob
from scipy.signal import hilbert, coherence, butter, filtfilt
import plotly.graph_objects as go
import plotly.express as px

# Parameters
DATA_DIR = str(DATA_DIR)
CHECKPOINT_DIR = str(PROCESSED_DATA_DIR)
OUTPUT_DIR = str(FIGURES_DIR / 'final_reports/connectivity')

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    SESSIONS = ['230630', '230816', '230830']
    FS = 1000.0
    OMIT_ONSET = 4124
    WIN_SIZE = 500
    AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    def bandpass_filter(data, lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return filtfilt(b, a, data, axis=-1)
    def compute_ppc(phases):
    # Pairwise Phase Consistency
    n = len(phases)
    if n < 2: return 0
    # Average of dot products of all pairs
    # (sum_cos^2 + sum_sin^2 - n) / (n*(n-1))
    sum_cos = np.sum(np.cos(phases))
    sum_sin = np.sum(np.sin(phases))
    return (sum_cos**2 + sum_sin**2 - n) / (n * (n - 1))
    def run_adjacency_matrices():
    vflip_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'vflip2_mapping_v3.csv'))
    units_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    # Initialize Matrices (11x11)
    matrix_coh = np.zeros((11, 11))
    matrix_ppc = np.zeros((11, 11))
    matrix_amp = np.zeros((11, 11))
    counts = np.zeros((11, 11))
    for sid in SESSIONS:
        print(f"Adjacency Matrix: Session {sid}")
        session_vflip = vflip_df[vflip_df['session_id'] == int(sid)]
        session_units = units_df[units_df['session'] == int(sid)]
        probes = session_vflip['probe_id'].unique()
        probe_areas = {}
        probe_lfp = {}
        probe_spk = {}
        # 1. Load Data
        for p_id in probes:
            area_str = session_vflip[session_vflip['probe_id'] == p_id]['area'].values[0]
            clean_a = [a for a in AREA_ORDER if a in area_str]
            if not clean_a: continue
            area = clean_a[0]
            probe_areas[p_id] = area
            # Load LFP
            f_lfp = os.path.join(DATA_DIR, f'ses{sid}-probe{p_id}-lfp-AAAX.npy')
            if os.path.exists(f_lfp):
                crossover = session_vflip[session_vflip['probe_id'] == p_id]['crossover'].values[0]
                ch = int(crossover) if not np.isnan(crossover) else 64
                probe_lfp[area] = np.load(f_lfp, mmap_mode='r')[:, ch, OMIT_ONSET : OMIT_ONSET + WIN_SIZE]
            # Load Spikes (Mean Population)
            f_spk = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p_id}-spk-AAAX.npy')
            if os.path.exists(f_spk):
                probe_spk[area] = np.load(f_spk, mmap_mode='r')[:, :, OMIT_ONSET : OMIT_ONSET + WIN_SIZE]
        # 2. Compute Interactions
        for i, a1 in enumerate(AREA_ORDER):
            for j, a2 in enumerate(AREA_ORDER):
                if a1 in probe_lfp and a2 in probe_lfp:
                    # LFP-LFP Coherence (Gamma)
                    all_coh = []
                    for t in range(min(50, probe_lfp[a1].shape[0])):
                        f_v, Cxy = coherence(probe_lfp[a1][t, :], probe_lfp[a2][t, :], fs=FS, nperseg=256)
                        all_coh.append(np.mean(Cxy[(f_v >= 35) & (f_v <= 80)]))
                    matrix_coh[i, j] += np.mean(all_coh)
                    # Amp-Amp Correlation (Gamma Envelope)
                    all_corr = []
                    for t in range(min(50, probe_lfp[a1].shape[0])):
                        env1 = np.abs(hilbert(bandpass_filter(probe_lfp[a1][t, :], 35, 80, FS)))
                        env2 = np.abs(hilbert(bandpass_filter(probe_lfp[a2][t, :], 35, 80, FS)))
                        all_corr.append(np.corrcoef(env1, env2)[0, 1])
                    matrix_amp[i, j] += np.mean(all_corr)
                    # Spike-LFP Phase Locking (PPC)
                    # Use a2 LFP phase and a1 Spikes
                    if a1 in probe_spk:
                        all_ppc = []
                        for t in range(min(30, probe_lfp[a2].shape[0])):
                            phase = np.angle(hilbert(bandpass_filter(probe_lfp[a2][t, :], 4, 12, FS))) # Alpha/Theta phase
                            # For each neuron in a1
                            for u in range(probe_spk[a1].shape[1]):
                                spikes = probe_spk[a1][t, u, :] > 0
                                if np.any(spikes):
                                    all_ppc.append(compute_ppc(phase[spikes]))
                        if all_ppc: matrix_ppc[i, j] += np.mean(all_ppc)
                    counts[i, j] += 1
    # Normalize
    matrix_coh /= (counts + 1e-9)
    matrix_ppc /= (counts + 1e-9)
    matrix_amp /= (counts + 1e-9)
    # Plotting
    for name, mat in [('LFP_Coherence_Gamma', matrix_coh), 
                       ('Spike_LFP_PPC_Alpha', matrix_ppc), 
                       ('Amp_Envelope_Corr_Gamma', matrix_amp)]:
        fig = px.imshow(mat, x=AREA_ORDER, y=AREA_ORDER, color_continuous_scale='Viridis',
                        title=f"Figure 14: Network Adjacency Matrix - {name} (Omission AAAX)")
        fig.update_layout(xaxis_title="Target Area", yaxis_title="Source Area", template="plotly_white")
        fig.write_html(os.path.join(OUTPUT_DIR, f"FIG_14_{name}.html"))
        print(f"Saved {name} matrix.")
    run_adjacency_matrices()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
