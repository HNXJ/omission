
import numpy as np
import pandas as pd
import glob
import os
import json
import plotly.graph_objects as go
import re

OMISSION_WINDOW = (4093, 4624) # ms
LAG_RANGE = 200 # +/- 200 ms
BIN_SIZE = 1 # ms

def compute_ccg(spikes1, spikes2, lag_range_ms):
    """
    Computes Cross-Correlogram between two binary spike trains.
    spikes: (trials, time)
    """
    n_trials, n_time = spikes1.shape
    lags = np.arange(-lag_range_ms, lag_range_ms + 1)
    ccg = np.zeros(len(lags))
    
    for t in range(n_trials):
        s1 = spikes1[t, :]
        s2 = spikes2[t, :]
        
        # Using numpy correlate for fast computation
        # Mode 'full' gives lags from -(n_time-1) to (n_time-1)
        full_corr = np.correlate(s1, s2, mode='full')
        center = n_time - 1
        ccg += full_corr[center - lag_range_ms : center + lag_range_ms + 1]
        
    return lags, ccg / n_trials

def run_spike_connectivity():
    with open('checkpoints/omission_units_v1_pfc.json', 'r') as f:
        omission_units = json.load(f)
        
    os.makedirs('figures/connectivity', exist_ok=True)
    
    all_lags = []
    
    for session_id, areas in omission_units.items():
        v1_units = areas['V1']
        pfc_units = areas['PFC']
        
        if not v1_units or not pfc_units:
            print(f"Skipping session {session_id} (missing units in one area).")
            continue
            
        print(f"Computing CCG for session {session_id} ({len(v1_units)} V1 x {len(pfc_units)} PFC)...")
        
        # Load AAAX (Omission) and RRRR (Standard) for all probes involved
        all_probes = set([u['probe_id'] for u in v1_units] + [u['probe_id'] for u in pfc_units])
        data_aaax = {}
        data_aaaa = {}
        
        for p in all_probes:
            f_aaax = glob.glob(f'data/ses{session_id}-units-probe{p}-spk-AAAX.npy')[0]
            f_aaaa = glob.glob(f'data/ses{session_id}-units-probe{p}-spk-RRRR.npy')[0]
            data_aaax[p] = np.load(f_aaax, mmap_mode='r')
            data_aaaa[p] = np.load(f_aaaa, mmap_mode='r')
            
        session_ccg_om = np.zeros(2 * LAG_RANGE + 1)
        session_ccg_std = np.zeros(2 * LAG_RANGE + 1)
        pair_count = 0
        
        for v1_u in v1_units:
            v1_spk_om = data_aaax[v1_u['probe_id']][:, v1_u['unit_idx'], OMISSION_WINDOW[0]:OMISSION_WINDOW[1]]
            v1_spk_std = data_aaaa[v1_u['probe_id']][:, v1_u['unit_idx'], OMISSION_WINDOW[0]:OMISSION_WINDOW[1]]
            
            for pfc_u in pfc_units:
                pfc_spk_om = data_aaax[pfc_u['probe_id']][:, pfc_u['unit_idx'], OMISSION_WINDOW[0]:OMISSION_WINDOW[1]]
                pfc_spk_std = data_aaaa[pfc_u['probe_id']][:, pfc_u['unit_idx'], OMISSION_WINDOW[0]:OMISSION_WINDOW[1]]
                
                lags, ccg_om = compute_ccg(v1_spk_om, pfc_spk_om, LAG_RANGE)
                _, ccg_std = compute_ccg(v1_spk_std, pfc_spk_std, LAG_RANGE)
                
                session_ccg_om += ccg_om
                session_ccg_std += ccg_std
                pair_count += 1
                
        if pair_count > 0:
            session_ccg_om /= pair_count
            session_ccg_std /= pair_count
            
            # Plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=lags, y=session_ccg_om, mode='lines', name='Omission (AAAX)'))
            fig.add_trace(go.Scatter(x=lags, y=session_ccg_std, mode='lines', name='Standard (RRRR)'))
            
            fig.update_layout(
                title=f"V1-PFC Spike Cross-Correlogram (Session {session_id}, {pair_count} pairs)",
                xaxis_title="Lag (ms) [Negative: V1 leads PFC]",
                yaxis_title="Coincidence Count",
                template="plotly_white"
            )
            fig.write_html(f"figures/connectivity/ses-{session_id}_v1_pfc_ccg.html")
            
            # Find peak lag
            peak_lag_om = lags[np.argmax(session_ccg_om)]
            print(f"  - Session {session_id} peak lag (Omission): {peak_lag_om} ms")
            all_lags.append(peak_lag_om)

    if all_lags:
        print(f"\nAverage V1-PFC Peak Lag (Omission): {np.mean(all_lags):.2f} ms")


def main(args=None):
    run_spike_connectivity()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
