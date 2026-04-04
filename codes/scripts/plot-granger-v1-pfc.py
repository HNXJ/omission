
import numpy as np
import h5py
import nitime.analysis as nta
import nitime.timeseries as ts
import plotly.graph_objects as go
import os

SESSION_ID = '230816'
WIN_START = 4093
WIN_END = 4624
SAMPLING_RATE = 1000.0

def compute_granger():
    lfp_path = f'data/lfp_by_area_ses-{SESSION_ID}.h5'
    if not os.path.exists(lfp_path): return

    with h5py.File(lfp_path, 'r') as f:
        # Based on H5 inspection:
        # V3, V1 -> V1 is likely channels 64-127
        # PFC -> 128 channels
        
        # Get Mean LFP for V1 (sub-select channels 64-127)
        v1_omit_all = f['V3, V1']['AAAX'][:, 64:127, WIN_START:WIN_END]
        v1_omit = np.mean(v1_omit_all, axis=1) # (trials, time)
        
        pfc_omit_all = f['PFC']['AAAX'][:, :, WIN_START:WIN_END]
        pfc_omit = np.mean(pfc_omit_all, axis=1)
        
        v1_std_all = f['V3, V1']['RRRR'][:, 64:127, WIN_START:WIN_END]
        v1_std = np.mean(v1_std_all, axis=1)
        
        pfc_std_all = f['PFC']['RRRR'][:, :, WIN_START:WIN_END]
        pfc_std = np.mean(pfc_std_all, axis=1)

    def get_gc(a1, a2):
        data = np.stack([a1, a2])
        t_series = ts.TimeSeries(data, sampling_rate=SAMPLING_RATE)
        g_analysis = nta.GrangerAnalyzer(t_series, order=15)
        return g_analysis.frequencies, g_analysis.causality[1, 0], g_analysis.causality[0, 1]

    print("Computing Granger for Omission...")
    freqs, gc_v1_to_pfc_omit, gc_pfc_to_v1_omit = get_gc(v1_omit, pfc_omit)
    print("Computing Granger for Standard...")
    _, gc_v1_to_pfc_std, gc_pfc_to_v1_std = get_gc(v1_std, pfc_std)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freqs, y=gc_v1_to_pfc_omit, name='V1->PFC (Omit)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=freqs, y=gc_pfc_to_v1_omit, name='PFC->V1 (Omit)', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=freqs, y=gc_v1_to_pfc_std, name='V1->PFC (Std)', line=dict(color='pink', dash='dash')))
    fig.add_trace(go.Scatter(x=freqs, y=gc_pfc_to_v1_std, name='PFC->V1 (Std)', line=dict(color='lightblue', dash='dash')))

    fig.update_layout(title=f"V1-PFC Spectral Granger Causality (Ses {SESSION_ID})",
                      xaxis_title="Frequency (Hz)", yaxis_title="Granger Causality",
                      xaxis_range=[0, 100], template="plotly_white")
    
    os.makedirs('figures/final_reports', exist_ok=True)
    fig.write_html("figures/final_reports/FIG_06B_V1_PFC_Granger.html")
    print("Saved Figure 6B.")

if __name__ == '__main__':
    compute_granger()
