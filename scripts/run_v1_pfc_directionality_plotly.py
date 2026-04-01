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

# Aesthetic Constants
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
BLACK = '#000000'
SLATE = '#708090'
WHITE = '#FFFFFF'
RED = '#FF4B4B'
BLUE = '#1F77B4'

# Parameters
FS = 1000.0
LAG_RANGE = 200 # ms
# P4 Omission (P4 onset at 4093 in stimulus sequence)
# Stim sequence: fx (1000) -> p1 (531) -> d1 (500) -> p2 (531) -> d2 (500) -> p3 (531) -> d3 (500) -> p4 (531) -> d4 (500)
# p4 onset = 1000 (fx) + 531 + 500 + 531 + 500 + 531 + 500 = 4093.
OMIT_WIN = (4093, 4624) 
LFP_ORDER = 15

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\directionality'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compute_ccg_robust(spk1, spk2):
    """Computes trial-averaged CCG between two spike trains with smoothing."""
    # spk: (trials, units, time)
    n_trials = spk1.shape[0]
    n_time = spk1.shape[2]
    lags = np.arange(-LAG_RANGE, LAG_RANGE + 1)
    ccg_sum = np.zeros(len(lags))
    
    # Pool across units
    pop1 = np.mean(spk1, axis=1) # (trials, time)
    pop2 = np.mean(spk2, axis=1)
    
    for t in range(n_trials):
        c = correlate(pop1[t, :], pop2[t, :], mode='full')
        mid = len(c) // 2
        ccg_sum += c[mid - LAG_RANGE : mid + LAG_RANGE + 1]
    
    return lags, ccg_sum / n_trials

def run_v1_pfc_directionality():
    # Load categories to find V1 and PFC probes
    # Using neuron_categories.csv for broad area mapping
    cat_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    sessions = cat_df['session'].unique()
    
    all_results = []
    
    for sid in sessions:
        sid_str = str(sid)
        ses_units = cat_df[cat_df['session'] == sid]
        
        v1_units = ses_units[ses_units['area'].str.contains('V1', na=False)]
        pfc_units = ses_units[ses_units['area'].str.contains('PFC', na=False)]
        
        if v1_units.empty or pfc_units.empty:
            continue
            
        print(f"--- Directionality: Session {sid_str} (V1 vs PFC) ---")
        
        v1_probe = v1_units['probe'].iloc[0]
        pfc_probe = pfc_units['probe'].iloc[0]
        
        # Conditions: AAAX (Omission) and RRRR (Standard)
        conds = ['AAAX', 'RRRR']
        results = {}
        
        for c in conds:
            try:
                # 1. SPIKES
                v1_spk_path = os.path.join(DATA_DIR, f'ses{sid_str}-units-probe{v1_probe}-spk-{c}.npy')
                pfc_spk_path = os.path.join(DATA_DIR, f'ses{sid_str}-units-probe{pfc_probe}-spk-{c}.npy')
                
                if os.path.exists(v1_spk_path) and os.path.exists(pfc_spk_path):
                    v1_spk = np.load(v1_spk_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]]
                    pfc_spk = np.load(pfc_spk_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]]
                    lags, ccg = compute_ccg_robust(v1_spk, pfc_spk)
                    results[f'ccg_{c}'] = ccg
                
                # 2. LFP
                v1_lfp_path = os.path.join(DATA_DIR, f'ses{sid_str}-probe{v1_probe}-lfp-{c}.npy')
                pfc_lfp_path = os.path.join(DATA_DIR, f'ses{sid_str}-probe{pfc_probe}-lfp-{c}.npy')
                
                if os.path.exists(v1_lfp_path) and os.path.exists(pfc_lfp_path):
                    v1_lfp = np.mean(np.load(v1_lfp_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]], axis=1)
                    pfc_lfp = np.mean(np.load(pfc_lfp_path, mmap_mode='r')[:, :, OMIT_WIN[0]:OMIT_WIN[1]], axis=1)
                    
                    # Trial-averaged LFP for Granger (more robust if trials are consistent)
                    data = np.stack([v1_lfp.mean(axis=0), pfc_lfp.mean(axis=0)])
                    t_series = ts.TimeSeries(data, sampling_rate=FS)
                    g_analyzer = nta.GrangerAnalyzer(t_series, order=LFP_ORDER)
                    
                    results[f'freqs_{c}'] = g_analyzer.frequencies
                    results[f'g_v1_pfc_{c}'] = g_analyzer.causality_xy
                    results[f'g_pfc_v1_{c}'] = g_analyzer.causality_yx
            except Exception as e:
                print(f"  Error processing {c} for {sid_str}: {e}")
        
        # Plotting for this session
        if f'ccg_AAAX' in results:
            fig_ccg = go.Figure()
            fig_ccg.add_trace(go.Scatter(x=lags, y=results['ccg_AAAX'], name='Omit (AAAX)', line=dict(color=GOLD, width=3)))
            fig_ccg.add_trace(go.Scatter(x=lags, y=results['ccg_RRRR'], name='Std (RRRR)', line=dict(color=SLATE, dash='dash')))
            fig_ccg.update_layout(template='plotly_dark', title=f"Directionality (Spike CCG): {sid_str} (V1 vs PFC)",
                                  xaxis_title="Lag (ms) [V1 leads PFC if peak > 0]", yaxis_title="Coincidence Count",
                                  paper_bgcolor=BLACK, plot_bgcolor=BLACK)
            fig_ccg.write_html(os.path.join(OUTPUT_DIR, f"DIR_CCG_{sid_str}_V1_PFC.html"))
            
        if f'g_v1_pfc_AAAX' in results:
            fig_g = go.Figure()
            f = results['freqs_AAAX']
            
            def clean(x):
                return np.where(np.isnan(x) | np.isinf(x), 0, x)
                
            fig_g.add_trace(go.Scatter(x=f, y=clean(results['g_v1_pfc_AAAX']), name='V1 -> PFC (Omit)', line=dict(color=GOLD)))
            fig_g.add_trace(go.Scatter(x=f, y=clean(results['g_pfc_v1_AAAX']), name='PFC -> V1 (Omit)', line=dict(color=VIOLET)))
            fig_g.add_trace(go.Scatter(x=f, y=clean(results['g_v1_pfc_RRRR']), name='V1 -> PFC (Std)', line=dict(color=GOLD, dash='dash'), opacity=0.5))
            fig_g.add_trace(go.Scatter(x=f, y=clean(results['g_pfc_v1_RRRR']), name='PFC -> V1 (Std)', line=dict(color=VIOLET, dash='dash'), opacity=0.5))
            fig_g.update_layout(template='plotly_dark', title=f"Directionality (Spectral Granger): {sid_str} (V1 vs PFC)",
                                xaxis_title="Frequency (Hz)", yaxis_title="Causality",
                                xaxis_range=[0, 100], paper_bgcolor=BLACK, plot_bgcolor=BLACK)
            fig_g.write_html(os.path.join(OUTPUT_DIR, f"DIR_Granger_{sid_str}_V1_PFC.html"))
        
        all_results.append(results)
            
    # Aggregate across sessions
    if all_results:
        summary_ccg_om = np.mean([r['ccg_AAAX'] for r in all_results if 'ccg_AAAX' in r], axis=0)
        summary_ccg_std = np.mean([r['ccg_RRRR'] for r in all_results if 'ccg_RRRR' in r], axis=0)
        
        fig_ccg_sum = go.Figure()
        fig_ccg_sum.add_trace(go.Scatter(x=lags, y=summary_ccg_om, name='Omit (AAAX)', line=dict(color=GOLD, width=4)))
        fig_ccg_sum.add_trace(go.Scatter(x=lags, y=summary_ccg_std, name='Std (RRRR)', line=dict(color=SLATE, dash='dash')))
        fig_ccg_sum.update_layout(template='plotly_dark', title="Figure 06A: V1-PFC Spike CCG (Summary)",
                                  xaxis_title="Lag (ms) [V1 leads PFC if peak > 0]", yaxis_title="Coincidence Count",
                                  paper_bgcolor=BLACK, plot_bgcolor=BLACK)
        fig_ccg_sum.write_html(os.path.join(OUTPUT_DIR, "FIG_06A_V1_PFC_CCG_Summary.html"))
        
        # Granger Summary
        # ... similar for Granger ...
        summary_g_v1_pfc_om = np.mean([r['g_v1_pfc_AAAX'] for r in all_results if 'g_v1_pfc_AAAX' in r], axis=0)
        summary_g_pfc_v1_om = np.mean([r['g_pfc_v1_AAAX'] for r in all_results if 'g_pfc_v1_AAAX' in r], axis=0)
        
        fig_g_sum = go.Figure()
        fig_g_sum.add_trace(go.Scatter(x=f, y=clean(summary_g_v1_pfc_om), name='V1 -> PFC (Omit)', line=dict(color=GOLD, width=3)))
        fig_g_sum.add_trace(go.Scatter(x=f, y=clean(summary_g_pfc_v1_om), name='PFC -> V1 (Omit)', line=dict(color=VIOLET, width=3)))
        fig_g_sum.update_layout(template='plotly_dark', title="Figure 06B: V1-PFC Spectral Granger (Summary)",
                                xaxis_title="Frequency (Hz)", yaxis_title="Causality",
                                xaxis_range=[0, 100], paper_bgcolor=BLACK, plot_bgcolor=BLACK)
        fig_g_sum.write_html(os.path.join(OUTPUT_DIR, "FIG_06B_V1_PFC_Granger_Summary.html"))

    print("Directionality Analysis Complete.")

if __name__ == '__main__':
    run_v1_pfc_directionality()
