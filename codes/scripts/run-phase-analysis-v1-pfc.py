
import numpy as np
import glob
import os
import plotly.graph_objects as go
from scipy.signal import coherence, csd
import re

OMISSION_WINDOW = (4093, 4624)
SAMPLING_RATE = 1000.0

def compute_phase_lag(sig1, sig2, fs):
    """
    Computes coherence and phase lag between two signals.
    sig: (trials, time)
    """
    # Average signals over trials for stability
    s1 = np.mean(sig1, axis=0)
    s2 = np.mean(sig2, axis=0)
    
    # Cross-spectral density
    f, Pxy = csd(s1, s2, fs=fs, nperseg=256)
    # Coherence
    f, Cxy = coherence(s1, s2, fs=fs, nperseg=256)
    
    # Phase lag (angle of cross-spectrum)
    phase = np.angle(Pxy)
    
    return f, Cxy, phase

def run_phase_analysis():
    target_sessions = ['230630', '230816', '230830']
    os.makedirs('figures/connectivity', exist_ok=True)
    
    print("\n--- LFP Coherence & Phase Lag Results (Omission) ---")
    
    for session_id in target_sessions:
        try:
            f_v1 = glob.glob(f'data/ses{session_id}-probe2-lfp-AAAX.npy')[0]
            f_pfc = glob.glob(f'data/ses{session_id}-probe0-lfp-AAAX.npy')[0]
            
            lfp_v1_all = np.load(f_v1, mmap_mode='r')
            lfp_pfc_all = np.load(f_pfc, mmap_mode='r')
            
            # Average across channels
            lfp_v1 = np.mean(lfp_v1_all[:, :, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]], axis=1)
            lfp_pfc = np.mean(lfp_pfc_all[:, :, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]], axis=1)
            
            f, Cxy, phase = compute_phase_lag(lfp_v1, lfp_pfc, SAMPLING_RATE)
            
            # Plot
            from plotly.subplots import make_subplots
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Coherence", "Phase Lag (Radians)"))
            
            fig.add_trace(go.Scatter(x=f, y=Cxy, mode='lines', name='Coherence'), row=1, col=1)
            fig.add_trace(go.Scatter(x=f, y=phase, mode='lines', name='Phase Lag (V1 relative to PFC)'), row=2, col=1)
            
            fig.update_layout(
                title=f"V1-PFC LFP Interaction (Session {session_id}, Omission)",
                xaxis_range=[0, 100],
                xaxis2_range=[0, 100],
                template="plotly_white",
                height=700
            )
            fig.write_html(f"figures/connectivity/ses-{session_id}_v1_pfc_phase.html")
            
            # Key band summary (Gamma: 35-70Hz)
            gamma_mask = (f >= 35) & (f <= 70)
            beta_mask = (f >= 13) & (f <= 30)
            
            avg_phase_gamma = np.mean(phase[gamma_mask])
            dir_gamma = "V1 leads PFC" if avg_phase_gamma < 0 else "PFC leads V1"
            
            avg_phase_beta = np.mean(phase[beta_mask])
            dir_beta = "V1 leads PFC" if avg_phase_beta < 0 else "PFC leads V1"
            
            print(f"Session {session_id}:")
            print(f"  - BETA  Coherence: {np.mean(Cxy[beta_mask]):.4f}, Phase: {avg_phase_beta:.4f} rad [{dir_beta}]")
            print(f"  - GAMMA Coherence: {np.mean(Cxy[gamma_mask]):.4f}, Phase: {avg_phase_gamma:.4f} rad [{dir_gamma}]")
            
        except Exception as e:
            print(f"  - Error session {session_id}: {e}")

if __name__ == '__main__':
    run_phase_analysis()
