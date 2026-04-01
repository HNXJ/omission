
import numpy as np
import pandas as pd
import h5py
import nitime.analysis as nta
import nitime.timeseries as ts
import plotly.graph_objects as go
from scipy.signal import correlate
import os
import glob
import re

# Parameters
SESSIONS = ['230630', '230816', '230830']
FS = 1000.0
LAG_RANGE = 200 # ms
OMIT_WIN = (4093, 4624) # Sample indices for 0-531ms post-p2 omission
STD_WIN = (4093, 4624) # Same window in RRRR trials (post-p2)
LFP_ORDER = 15 # Granger order

# Paths
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compute_ccg(spk1, spk2):
    """Computes trial-averaged CCG between two spike trains."""
    # Shapes: (trials, time)
    n_trials = spk1.shape[0]
    lags = np.arange(-LAG_RANGE, LAG_RANGE + 1)
    ccg_sum = np.zeros(len(lags))
    
    for t in range(n_trials):
        c = correlate(spk1[t, :], spk2[t, :], mode='full')
        mid = len(c) // 2
        ccg_sum += c[mid - LAG_RANGE : mid + LAG_RANGE + 1]
    
    return lags, ccg_sum / n_trials

def run_directionality():
    # Load Neuron Categories for V1-PFC unit selection
    units_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    
    all_ccg_om = []
    all_ccg_std = []
    
    all_granger_om = {'v1_pfc': [], 'pfc_v1': []}
    all_granger_std = {'v1_pfc': [], 'pfc_v1': []}
    freqs = None

    for sid in SESSIONS:
        print(f"Processing Session {sid}...")
        
        # 1. SPIKE CCG
        v1_units = units_df[(units_df['session'] == int(sid)) & (units_df['area'].str.contains('V1'))]
        pfc_units = units_df[(units_df['session'] == int(sid)) & (units_df['area'].str.contains('PFC'))]
        
        if len(v1_units) > 0 and len(pfc_units) > 0:
            # Get spike data (AAA X vs RRRR)
            # Find probe IDs
            v1_probes = v1_units['probe'].unique()
            pfc_probes = pfc_units['probe'].unique()
            
            # Simplified: Use first probe with V1 and PFC for each
            # Actually, let's aggregate all pairs
            for vp in v1_probes:
                for pp in pfc_probes:
                    try:
                        v1_spk_om_path = os.path.join(DATA_DIR, f'ses{sid}-units-probe{vp}-spk-AAAX.npy')
                        pfc_spk_om_path = os.path.join(DATA_DIR, f'ses{sid}-units-probe{pp}-spk-AAAX.npy')
                        v1_spk_std_path = os.path.join(DATA_DIR, f'ses{sid}-units-probe{vp}-spk-RRRR.npy')
                        pfc_spk_std_path = os.path.join(DATA_DIR, f'ses{sid}-units-probe{pp}-spk-RRRR.npy')
                        
                        v1_spk_om = np.load(v1_spk_om_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]]
                        pfc_spk_om = np.load(pfc_spk_om_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]]
                        v1_spk_std = np.load(v1_spk_std_path, mmap_mode='r')[:, :, STD_WIN[0]:STD_WIN[1]]
                        pfc_spk_std = np.load(pfc_spk_std_path, mmap_mode='r')[:, :, STD_WIN[0]:STD_WIN[1]]
                        
                        # Mean over units in that probe
                        v1_pop_om = np.mean(v1_spk_om, axis=1)
                        pfc_pop_om = np.mean(pfc_spk_om, axis=1)
                        v1_pop_std = np.mean(v1_spk_std, axis=1)
                        pfc_pop_std = np.mean(pfc_spk_std, axis=1)
                        
                        lags, ccg_om = compute_ccg(v1_pop_om, pfc_pop_om)
                        _, ccg_std = compute_ccg(v1_pop_std, pfc_pop_std)
                        
                        all_ccg_om.append(ccg_om)
                        all_ccg_std.append(ccg_std)
                    except Exception as e:
                        print(f"  Error loading spikes for {sid} V1-P{vp}/PFC-P{pp}: {e}")
        
        # 2. LFP GRANGER
        v1_probes = v1_units['probe'].unique()
        pfc_probes = pfc_units['probe'].unique()
        
        if len(v1_probes) > 0 and len(pfc_probes) > 0:
            vp, pp = v1_probes[0], pfc_probes[0]
            try:
                v1_lfp_om_path = os.path.join(DATA_DIR, f'ses{sid}-probe{vp}-lfp-AAAX.npy')
                pfc_lfp_om_path = os.path.join(DATA_DIR, f'ses{sid}-probe{pp}-lfp-AAAX.npy')
                v1_lfp_std_path = os.path.join(DATA_DIR, f'ses{sid}-probe{vp}-lfp-RRRR.npy')
                pfc_lfp_std_path = os.path.join(DATA_DIR, f'ses{sid}-probe{pp}-lfp-RRRR.npy')
                
                v1_lfp_om = np.mean(np.load(v1_lfp_om_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]], axis=1)
                pfc_lfp_om = np.mean(np.load(pfc_lfp_om_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]], axis=1)
                v1_lfp_std = np.mean(np.load(v1_lfp_std_path, mmap_mode='r')[:, :, STD_WIN[0]:STD_WIN[1]], axis=1)
                pfc_lfp_std = np.mean(np.load(pfc_lfp_std_path, mmap_mode='r')[:, :, STD_WIN[0]:STD_WIN[1]], axis=1)
                
                # Spectral Granger
                def get_granger(a1, a2):
                    data = np.stack([a1.mean(axis=0), a2.mean(axis=0)])
                    t_series = ts.TimeSeries(data, sampling_rate=FS)
                    g_analyzer = nta.GrangerAnalyzer(t_series, order=LFP_ORDER)
                    return g_analyzer.frequencies, g_analyzer.causality_xy, g_analyzer.causality_yx
                
                freqs, v1_pfc_om, pfc_v1_om = get_granger(v1_lfp_om, pfc_lfp_om)
                _, v1_pfc_std, pfc_v1_std = get_granger(v1_lfp_std, pfc_lfp_std)
                
                all_granger_om['v1_pfc'].append(v1_pfc_om)
                all_granger_om['pfc_v1'].append(pfc_v1_om)
                all_granger_std['v1_pfc'].append(v1_pfc_std)
                all_granger_std['pfc_v1'].append(pfc_v1_std)
            except Exception as e:
                print(f"  Error computing Granger for {sid} V1-P{vp}/PFC-P{pp}: {e}")

    # Aggregation
    if all_ccg_om:
        mean_ccg_om = np.mean(all_ccg_om, axis=0)
        mean_ccg_std = np.mean(all_ccg_std, axis=0)
        
        fig_ccg = go.Figure()
        fig_ccg.add_trace(go.Scatter(x=lags, y=mean_ccg_om, name='Omission (AAAX)', line=dict(color='darkred')))
        fig_ccg.add_trace(go.Scatter(x=lags, y=mean_ccg_std, name='Standard (RRRR)', line=dict(color='gray', dash='dash')))
        fig_ccg.update_layout(title="Figure 06A: V1-PFC Spike CCG (Directionality Analysis)",
                              xaxis_title="Lag (ms) [V1 leads PFC if peak > 0]", yaxis_title="Coincidence Count (Trial Avg)",
                              template="plotly_white")
        fig_ccg.write_html(os.path.join(OUTPUT_DIR, "FIG_06A_V1_PFC_CCG.html"))
        print("Saved FIG_06A.")

    if all_granger_om['v1_pfc']:
        mean_v1_pfc_om = np.mean(all_granger_om['v1_pfc'], axis=0)
        mean_pfc_v1_om = np.mean(all_granger_om['pfc_v1'], axis=0)
        mean_v1_pfc_std = np.mean(all_granger_std['v1_pfc'], axis=0)
        mean_pfc_v1_std = np.mean(all_granger_std['pfc_v1'], axis=0)
        
        fig_g = go.Figure()
        fig_g.add_trace(go.Scatter(x=freqs, y=mean_v1_pfc_om, name='V1 -> PFC (Omit)', line=dict(color='red')))
        fig_g.add_trace(go.Scatter(x=freqs, y=mean_pfc_v1_om, name='PFC -> V1 (Omit)', line=dict(color='blue')))
        fig_g.add_trace(go.Scatter(x=freqs, y=mean_v1_pfc_std, name='V1 -> PFC (Std)', line=dict(color='pink', dash='dash')))
        fig_g.add_trace(go.Scatter(x=freqs, y=mean_pfc_v1_std, name='PFC -> V1 (Std)', line=dict(color='lightblue', dash='dash')))
        
        fig_g.update_layout(title="Figure 06B: V1-PFC Spectral Granger Causality (LFP)",
                            xaxis_title="Frequency (Hz)", yaxis_title="Granger Causality",
                            xaxis_range=[0, 100], template="plotly_white")
        fig_g.write_html(os.path.join(OUTPUT_DIR, "FIG_06B_V1_PFC_Granger.html"))
        print("Saved FIG_06B.")

if __name__ == '__main__':
    run_directionality()
