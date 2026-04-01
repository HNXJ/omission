
import h5py
import numpy as np
import os
import glob
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import spectrogram

# --- Constants ---
DATA_DIR = 'data'
OUTPUT_DIR = 'figures/oglo/fig_06_LFP_dB_EXT_ALLSESSIONS'
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
FS = 1000.0

OMISSION_GROUPS = {
    'p2_omission': ['AXAB', 'BXBA', 'RXRR'],
    'p3_omission': ['AAXB', 'BBXA', 'RRXR']
}
BASELINE_WINDOW = (0, 1000)

BANDS = {
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 80)
}
OMISSION_TIME_WINDOWS = {'p2_omission':(1031,1562), 'p3_omission':(1562,2062)}


def load_lfp_data():
    h5_files = glob.glob(os.path.join(DATA_DIR, 'lfp_by_area_ses-*.h5'))
    all_lfp_data = {area: {group: [] for group in OMISSION_GROUPS} for area in TARGET_AREAS}
    for fpath in h5_files:
        with h5py.File(fpath, 'r') as f:
            for area_key in f.keys():
                areas_in_key = [a.strip() for a in area_key.split(',')]
                for group_name, cond_list in OMISSION_GROUPS.items():
                    for cond in cond_list:
                        if cond in f[area_key]:
                            avg_channel_traces = np.mean(f[area_key][cond][:], axis=1)
                            for area in areas_in_key:
                                if area in TARGET_AREAS:
                                    all_lfp_data[area][group_name].extend(avg_channel_traces)
    return all_lfp_data

def process_and_plot(lfp_data):
    for group_name in OMISSION_GROUPS:
        print(f"--- Processing Omission Group: {group_name} ---")
        
        # Store band-averaged power traces for each area
        power_traces_by_band = {band: {area: [] for area in TARGET_AREAS} for band in BANDS}
        
        for area in TARGET_AREAS:
            trials = lfp_data[area][group_name]
            if not trials: continue

            nperseg, noverlap = 256, int(0.98 * 256)
            
            for trial_trace in trials:
                bl_start, bl_end = BASELINE_WINDOW
                f, _, Sxx_bl = spectrogram(trial_trace[bl_start:bl_end], fs=FS, window='hann', nperseg=nperseg, noverlap=noverlap)
                mean_bl_power = np.mean(Sxx_bl, axis=1)

                f, t, Sxx = spectrogram(trial_trace, fs=FS, window='hann', nperseg=nperseg, noverlap=noverlap)
                Sxx_db = 10 * np.log10(Sxx / (mean_bl_power[:, np.newaxis] + 1e-12) + 1e-12)

                for band, (f_low, f_high) in BANDS.items():
                    freq_idx = np.where((f >= f_low) & (f <= f_high))[0]
                    if len(freq_idx) > 0:
                        band_power_trace = np.mean(Sxx_db[freq_idx, :], axis=0)
                        power_traces_by_band[band][area].append(band_power_trace)
        
        time_ms = (t * 1000) - 1000

        # Plot 1: Time-series power traces
        fig1 = make_subplots(rows=len(BANDS), cols=1, shared_xaxes=True, subplot_titles=list(BANDS.keys()))
        for i, (band, area_traces) in enumerate(power_traces_by_band.items()):
            for area, traces in area_traces.items():
                if not traces: continue
                mean_trace = np.mean(traces, axis=0)
                sem_trace = np.std(traces, axis=0) / np.sqrt(len(traces))
                
                fig1.add_trace(go.Scatter(x=time_ms, y=mean_trace, name=area, legendgroup=area, showlegend=(i==0)), row=i+1, col=1)
                fig1.add_trace(go.Scatter(x=np.concatenate([time_ms, time_ms[::-1]]), y=np.concatenate([mean_trace - 2*sem_trace, (mean_trace + 2*sem_trace)[::-1]]), fill='toself', opacity=0.2, line=dict(color='rgba(255,255,255,0)'), showlegend=False, legendgroup=area), row=i+1, col=1)
        
        fig1.update_layout(title=f'LFP Power Band Traces for {group_name}', template='plotly_white')
        fig1.write_html(os.path.join(OUTPUT_DIR, f"{group_name}_band_power_traces.html"))
        fig1.write_image(os.path.join(OUTPUT_DIR, f"{group_name}_band_power_traces.svg"))

        # Plot 2: Sorted bar chart of power change
        fig2 = make_subplots(rows=len(BANDS), cols=1, subplot_titles=[f"{band} Power Change" for band in BANDS])
        
        omit_start, omit_end = OMISSION_TIME_WINDOWS[group_name]
        time_idx = np.where((time_ms >= omit_start-1000) & (time_ms <= omit_end-1000))[0]

        for i, (band, area_traces) in enumerate(power_traces_by_band.items()):
            power_changes = {}
            for area, traces in area_traces.items():
                if traces:
                    mean_power_in_window = np.mean(np.array(traces)[:, time_idx])
                    power_changes[area] = mean_power_in_window
            
            sorted_areas = sorted(power_changes.items(), key=lambda item: item[1], reverse=True)
            
            fig2.add_trace(go.Bar(x=[item[0] for item in sorted_areas], y=[item[1] for item in sorted_areas], name=band), row=i+1, col=1)

        fig2.update_layout(title=f'Sorted LFP Power Change in Omission Window ({group_name})', template='plotly_white')
        fig2.write_html(os.path.join(OUTPUT_DIR, f"{group_name}_sorted_power_change.html"))
        fig2.write_image(os.path.join(OUTPUT_DIR, f"{group_name}_sorted_power_change.svg"))

if __name__ == '__main__':
    lfp_data = load_lfp_data()
    process_and_plot(lfp_data)
    print("Figure 6 generation complete.")

