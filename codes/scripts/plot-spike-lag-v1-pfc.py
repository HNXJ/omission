
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from scipy.signal import correlate
import re

# Cross-correlation window: +/- 250ms
MAX_LAG = 250
# Window: p4 omission (4093:4624)
WIN_START = 4093
WIN_END = 4624

def compute_spike_lag():
    # Load classifications
    cat_df = pd.read_csv('checkpoints/neuron_categories.csv')
    omit_v1 = cat_df[(cat_df['area'] == 'V1') & (cat_df['category'] == 'Omit')]
    omit_pfc = cat_df[(cat_df['area'] == 'PFC') & (cat_df['category'] == 'Omit')]

    if len(omit_v1) == 0 or len(omit_pfc) == 0:
        print("Insufficient V1 or PFC Omit-labeled units found.")
        return

    # Store all cross-correlograms
    all_ccgs = []

    # Iterate through sessions where both exist
    common_sessions = set(omit_v1['session']).intersection(set(omit_pfc['session']))
    
    for session_id in common_sessions:
        print(f"Computing V1-PFC CCG for session {session_id}...")
        s_v1 = omit_v1[omit_v1['session'] == int(session_id)]
        s_pfc = omit_pfc[omit_pfc['session'] == int(session_id)]
        
        # Load AAAX data (omission)
        f_v1 = glob.glob(f'data/ses{session_id}-units-probe*-spk-AAAX.npy')
        f_pfc = glob.glob(f'data/ses{session_id}-units-probe*-spk-AAAX.npy')
        
        # Mapping probe data
        probe_data = {}
        for f in f_v1:
            p_id = int(re.search(r'probe(\d+)', f).group(1))
            probe_data[p_id] = np.load(f, mmap_mode='r')

        for _, v1_unit in s_v1.iterrows():
            v1_p, v1_u = v1_unit['probe'], v1_unit['unit_idx']
            if v1_p not in probe_data: continue
            
            # Binary spike trains (trials, time)
            v1_spks = probe_data[v1_p][:, v1_u, WIN_START:WIN_END]
            
            for _, pfc_unit in s_pfc.iterrows():
                pfc_p, pfc_u = pfc_unit['probe'], pfc_unit['unit_idx']
                if pfc_p not in probe_data: continue
                
                pfc_spks = probe_data[pfc_p][:, pfc_u, WIN_START:WIN_END]
                
                # Cross-correlation trial-by-trial
                ccg_sum = np.zeros(2 * MAX_LAG + 1)
                num_trials = v1_spks.shape[0]
                
                for t in range(num_trials):
                    # Correlate V1 and PFC spikes
                    ccg = correlate(v1_spks[t, :], pfc_spks[t, :], mode='full')
                    mid = len(ccg) // 2
                    ccg_slice = ccg[mid - MAX_LAG : mid + MAX_LAG + 1]
                    ccg_sum += ccg_slice
                
                # Normalize CCG (mean over trials)
                all_ccgs.append(ccg_sum / num_trials)

    if not all_ccgs:
        print("No paired V1-PFC Omit units processed.")
        return

    # Average and Peak Detection
    grand_ccg = np.mean(all_ccgs, axis=0)
    lags = np.arange(-MAX_LAG, MAX_LAG + 1)
    peak_lag = lags[np.argmax(grand_ccg)]
    
    # Visualization
    os.makedirs('figures/final_reports', exist_ok=True)
    fig = go.Figure(data=[go.Bar(x=lags, y=grand_ccg, marker_color='darkblue')])
    fig.add_vline(x=0, line_dash="dash", line_color="black")
    fig.add_annotation(x=peak_lag, y=max(grand_ccg), text=f"Peak: {peak_lag}ms", showarrow=True)
    fig.update_layout(title=f"V1-PFC Spike-Spike Lag during Omission (Omit Units)",
                      xaxis_title="Lag (ms) [V1 leads if >0]", yaxis_title="Coincidence Count",
                      template="plotly_white")
    
    fig.write_html("figures/final_reports/FIG_06A_V1_PFC_Spike_Lag.html")
    try: fig.write_image("figures/final_reports/FIG_06A_V1_PFC_Spike_Lag.svg")
    except: pass
    
    print(f"Saved Figure 6A. Peak V1-PFC lag: {peak_lag}ms.")

if __name__ == '__main__':
    compute_spike_lag()
