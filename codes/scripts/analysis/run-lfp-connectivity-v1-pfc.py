
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
import nitime.analysis as na
import nitime.timeseries as ts
from pynwb import NWBHDF5IO
import re

OMISSION_WINDOW = (4093, 4624) # ms
SAMPLING_RATE = 1000.0 # Hz
ORDER = 15 # AR model order for Granger

def compute_spectral_granger(sig1, sig2, fs, order):
    """
    Computes spectral Granger Causality between two signals.
    sig: (trials, time)
    """
    # Combine signals for nitime
    # nitime expects (channels, time) for TimeSeries
    # We'll average over trials first for a simpler spectral estimate, 
    # OR better: use trial-based estimation if possible.
    
    # Method: Bivariate AR model
    combined = np.stack([sig1.mean(axis=0), sig2.mean(axis=0)])
    tseries = ts.TimeSeries(combined, sampling_rate=fs)
    
    # Granger Analyzer
    g_analyzer = na.GrangerAnalyzer(tseries, order=order)
    
    freqs = g_analyzer.frequencies
    # causality_xy is sig1 -> sig2
    # causality_yx is sig2 -> sig1
    g_12 = g_analyzer.causality_xy
    g_21 = g_analyzer.causality_yx
    
    return freqs, g_12, g_21

def run_lfp_connectivity():
    target_sessions = ['230630', '230816', '230830']
    os.makedirs('figures/connectivity', exist_ok=True)
    
    results = {}
    
    for session_id in target_sessions:
        print(f"Computing LFP Granger Causality for session {session_id}...")
        
        nwb_path = glob.glob(f'data/sub-*_ses-{session_id}_rec.nwb')[0]
        
        # Identify probes for V1 and PFC
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            elec_df = nwbfile.electrodes.to_dataframe()
            
            v1_probe = -1
            pfc_probe = -1
            
            # Simple check for labels
            for p in range(4):
                mask = (elec_df.index // 128 == p)
                if mask.any():
                    label = elec_df.loc[mask, 'location'].iloc[0]
                    if "V1" in label: v1_probe = p
                    if "PFC" in label: pfc_probe = p
            
            if v1_probe == -1 or pfc_probe == -1:
                print(f"  - Could not identify V1 and PFC probes in session {session_id}. Skipping.")
                continue
                
            print(f"  - V1 Probe: {v1_probe}, PFC Probe: {pfc_probe}")
            
            # Load LFP data for AAAX (Omission)
            # Match files like 'data/ses230818-probe0-lfp-AAAX.npy'
            try:
                f_v1 = glob.glob(f'data/ses{session_id}-probe{v1_probe}-lfp-AAAX.npy')[0]
                f_pfc = glob.glob(f'data/ses{session_id}-probe{pfc_probe}-lfp-AAAX.npy')[0]
                
                lfp_v1_all = np.load(f_v1, mmap_mode='r')
                lfp_pfc_all = np.load(f_pfc, mmap_mode='r')
                
                # Average across channels in the probe for a "local population" signal
                # Windows are same as spikes: (trials, channels, time)
                # OMISSION_WINDOW indices match time axis if start=0
                lfp_v1 = np.mean(lfp_v1_all[:, :, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]], axis=1)
                lfp_pfc = np.mean(lfp_pfc_all[:, :, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]], axis=1)
                
                freqs, g_v1_pfc, g_pfc_v1 = compute_spectral_granger(lfp_v1, lfp_pfc, SAMPLING_RATE, ORDER)
                
                # Plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=freqs, y=g_v1_pfc, mode='lines', name='V1 -> PFC (Feed-forward)'))
                fig.add_trace(go.Scatter(x=freqs, y=g_pfc_v1, mode='lines', name='PFC -> V1 (Feedback)'))
                
                fig.update_layout(
                    title=f"LFP Spectral Granger Causality (Session {session_id}, Omission)",
                    xaxis_title="Frequency (Hz)",
                    yaxis_title="Granger Causality Magnitude",
                    xaxis_range=[0, 100],
                    template="plotly_white"
                )
                fig.write_html(f"figures/connectivity/ses-{session_id}_v1_pfc_granger.html")
                print(f"  - Saved Granger plot for session {session_id}.")
                
            except Exception as e:
                print(f"  - Error processing session {session_id}: {e}")


def main(args=None):
    run_lfp_connectivity()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
