"""
generate_fig05_06_lfp_tfr.py
V4 Refinement: Omission-specific LFP windowing and summary.
Fig 05: Per condition windowed power traces (d1-p2-d2 or d2-p3-d3).
Fig 06: Average X2 (AXAB, BXBA, RXRR) and X3 (AAXB, BBXA, RRXR).
5 bands (Delta, Theta, Alpha, Beta, Gamma) + sorted bar plot.
Theme: plotly_white, Pink Omission patches, Triple Export.
"""
import os
import glob
import h5py
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import spectrogram
from plotly.subplots import make_subplots

# Configuration
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data\arrays'
OUTPUT_DIR_5 = r'D:\Analysis\Omission\local-workspace\figures\oglo\fig_05_LFP_power_traces'
OUTPUT_DIR_6 = r'D:\Analysis\Omission\local-workspace\figures\oglo\fig_06_LFP_bands_summary'
os.makedirs(OUTPUT_DIR_5, exist_ok=True)
os.makedirs(OUTPUT_DIR_6, exist_ok=True)

CONDITIONS = ['AAAB', 'AAAX', 'AAXB', 'AXAB', 'BBBA', 'BBBX', 'BBXA', 'BXBA', 'RRRR', 'RRRX', 'RRXR', 'RXRR']
X2_CONDS = ['AXAB', 'BXBA', 'RXRR']
X3_CONDS = ['AAXB', 'BBXA', 'RRXR']

BANDS = {
    'Delta': (1, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 150)
}
BAND_LIST = list(BANDS.keys())
CANONICAL_AREAS = ['V1', 'V2', 'V3', 'V4', 'MT', 'MST', 'TEO', 'FST', 'DP', 'PFC', 'FEF']
THEME_COLORS = ['#8F00FF', '#00FFCC', '#FF5E00', '#CFB87C', '#222222'] # Violet, Teal, Orange, Gold, Gray

def simplify_area(name):
    """Splits H5 keys like 'V4, TEO' and returns list of canonical areas."""
    name = name.upper().replace(' ', '')
    found = []
    for area in CANONICAL_AREAS:
        if area in name:
            found.append(area)
    return found

def get_lfp_data(session_id, condition):
    h5_path = os.path.join(DATA_DIR, f'lfp_by_area_ses-{session_id}.h5')
    if not os.path.exists(h5_path): return None
    results = {} # {canonical_area: data}
    try:
        with h5py.File(h5_path, 'r') as f:
            for k in f.keys():
                areas = simplify_area(k)
                if condition in f[k]:
                    data = np.nan_to_num(f[k][condition][:], nan=0.0, posinf=0.0, neginf=0.0)
                    for a in areas:
                        results[a] = data
    except: pass
    return results

def compute_band_traces(data, window_slice):
    """Computes power traces for a window [start, end]."""
    # data: (n_trials, n_channels, 6000)
    # Average over channels
    signal = np.nanmean(data[:, :, window_slice[0]:window_slice[1]], axis=1) # (n_trials, time)
    n_trials, n_time = signal.shape
    
    nperseg = 128 # 128ms window
    noverlap = 118 # 10ms step
    
    traces = {band: [] for band in BANDS}
    t_out = None
    
    for tr in range(n_trials):
        f, t_spec, Sxx = spectrogram(signal[tr], fs=1000.0, nperseg=nperseg, noverlap=noverlap)
        t_out = t_spec * 1000.0 # ms relative to window start
        for band, (f_low, f_high) in BANDS.items():
            f_mask = (f >= f_low) & (f <= f_high)
            traces[band].append(np.mean(Sxx[f_mask, :], axis=0))
            
    results = {}
    for band in BANDS:
        arr = np.array(traces[band])
        # (n_trials, n_time_bins)
        mean_pow = np.nanmean(arr, axis=0)
        sem_pow = np.nanstd(arr, axis=0) / np.sqrt(max(1, n_trials))
        results[band] = (t_out, mean_pow, sem_pow)
        
    return results

def run():
    print("Generating Figure 05 & 06: LFP TFR V4...")
    
    # To store pooled data for Fig 06
    pooled_traces = {area: {band: [] for band in BANDS} for area in CANONICAL_AREAS}
    
    h5_files = glob.glob(os.path.join(DATA_DIR, 'lfp_by_area_ses-*.h5'))
    sessions = [os.path.basename(f).split('-')[-1].replace('.h5', '') for f in h5_files]
    
    for cond in CONDITIONS:
        print(f"  - Processing {cond}...")
        
        # Dynamic Window
        if cond in X2_CONDS: window = (1531, 3062) # d1-p2-d2
        elif cond in X3_CONDS: window = (2562, 4093) # d2-p3-d3
        else: window = (1000, 2531) # Default to P1-D1-P2 range
        
        # Pink Omission relative to window start
        # Omission is always the second "pulse" in these windows? 
        # For X2: Omission P2 is 2031-2562. Window 1531-3062. Rel: 500-1031.
        # For X3: Omission P3 is 3062-3593. Window 2562-4093. Rel: 500-1031.
        om_start_rel, om_end_rel = 500, 1031
        
        area_means = {area: {band: [] for band in BANDS} for area in CANONICAL_AREAS}
        
        for ses in sessions:
            res_dict = get_lfp_data(ses, cond)
            if not res_dict: continue
            
            for area, data in res_dict.items():
                if area in CANONICAL_AREAS:
                    band_results = compute_band_traces(data, window)
                    for band in BANDS:
                        area_means[area][band].append(band_results[band][1])
                        if cond in X2_CONDS or cond in X3_CONDS:
                            pooled_traces[area][band].append(band_results[band][1])

        # Figure 05: Power traces per area for this condition
        active_areas = [a for a in CANONICAL_AREAS if any(len(area_means[a][b]) > 0 for b in BANDS)]
        if not active_areas: continue
        
        n_active = len(active_areas)
        fig5 = make_subplots(rows=(n_active+2)//3, cols=3, subplot_titles=active_areas)
        
        for i, area in enumerate(active_areas):
            r, c = i // 3 + 1, i % 3 + 1
            for j, band in enumerate(BAND_LIST):
                if area_means[area][band]:
                    m = np.nanmean(area_means[area][band], axis=0)
                    t = np.linspace(0, window[1]-window[0], len(m))
                    fig5.add_trace(go.Scatter(x=t, y=m, name=band, line=dict(color=THEME_COLORS[j%len(THEME_COLORS)]), showlegend=(i==0)), row=r, col=c)
            
            # Pink Omission Patch
            if cond in X2_CONDS or cond in X3_CONDS:
                fig5.add_vrect(x0=om_start_rel, x1=om_end_rel, fillcolor="#FF1493", opacity=0.15, layer="below", line_width=0, row=r, col=c)

        fig5.update_layout(title=f"<b>Fig 05: LFP Power Traces ({cond})</b><br><sup>Window: {window[0]}-{window[1]}ms</sup>", template="plotly_white", height=300*((n_active+2)//3))
        base5 = os.path.join(OUTPUT_DIR_5, f"fig_05_LFP_power_{cond}")
        fig5.write_html(base5 + ".html"); fig5.write_image(base5 + ".svg"); fig5.write_image(base5 + ".png")

    # Figure 06: Average X2 and X3
    print("  - Generating Fig 06 Summary...")
    fig6 = make_subplots(rows=3, cols=2, subplot_titles=BAND_LIST + ["Gamma Omission Response (dB)"])
    
    bar_results = []
    for i, band in enumerate(BAND_LIST):
        r, c = i // 2 + 1, i % 2 + 1
        for area in CANONICAL_AREAS:
            if pooled_traces[area][band]:
                m = np.nanmean(pooled_traces[area][band], axis=0)
                t = np.linspace(0, 1531, len(m))
                fig6.add_trace(go.Scatter(x=t, y=m, name=area, showlegend=(i==0), legendgroup=area), row=r, col=c)
                
                # Compute dB change for bar plot (P3/P2 vs D1/D2)
                # Baseline: 0-500ms (D1 or D2), Omission: 500-1031ms (P2 or P3)
                idx_base = t < 500
                idx_om = (t >= 500) & (t <= 1031)
                base_val = np.nanmean(m[idx_base])
                om_val = np.nanmean(m[idx_om])
                db = 10 * np.log10(om_val / (base_val + 1e-12))
                bar_results.append({'Area': area, 'Band': band, 'dB': db})
        
        # Add pink omission patch to summary plots
        fig6.add_vrect(x0=500, x1=1031, fillcolor="#FF1493", opacity=0.15, layer="below", line_width=0, row=r, col=c)

    # Sorted bar plot for Gamma
    df_bar = pd.DataFrame(bar_results)
    if not df_bar.empty:
        gamma_df = df_bar[df_bar['Band'] == 'Gamma'].sort_values('dB')
        fig6.add_trace(go.Bar(x=gamma_df['dB'], y=gamma_df['Area'], orientation='h', marker_color='#8F00FF', name='Gamma dB Change'), row=3, col=2)

    fig6.update_layout(height=1200, title="<b>Fig 06: LFP Omission Summary (Pooled X2 & X3)</b>", template="plotly_white")
    base6 = os.path.join(OUTPUT_DIR_6, "fig_06_LFP_Summary_V4")
    fig6.write_html(base6 + ".html"); fig6.write_image(base6 + ".svg"); fig6.write_image(base6 + ".png")
    
    print(f"LFP TFR V4 generation completed.")

if __name__ == '__main__':
    run()
