
import h5py
import numpy as np
import os
import glob
import re
import plotly.graph_objects as go
from scipy.signal import spectrogram

# --- Constants ---
DATA_DIR = 'data'
OUTPUT_DIR = 'figures/oglo/fig_05_LFP_dB_EXT_ALLSESSIONS'
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
FS = 1000.0  # Sampling frequency

OMISSION_GROUPS = {
    'p2_omission': ['AXAB', 'BXBA', 'RXRR'],
    'p3_omission': ['AAXB', 'BBXA', 'RRXR']
}

ANALYSIS_WINDOWS = {
    'p2_omission': (1531, 3062), # d1-p2-d2
    'p3_omission': (2562, 4093)  # d2-p3-d3
}
BASELINE_WINDOW = (0, 1000) # pre-stimulus period

def load_lfp_data():
    """Loads LFP data from H5 files for specified areas and conditions."""
    h5_files = glob.glob(os.path.join(DATA_DIR, 'lfp_by_area_ses-*.h5'))
    
    # Structure: data[area] = list of all trials from all relevant sessions/conditions
    all_lfp_data = {area: {group: [] for group in OMISSION_GROUPS} for area in TARGET_AREAS}

    for fpath in h5_files:
        print(f"Processing H5 file: {os.path.basename(fpath)}...")
        with h5py.File(fpath, 'r') as f:
            for area_key in f.keys():
                areas_in_key = [a.strip() for a in area_key.split(',')]
                for group_name, cond_list in OMISSION_GROUPS.items():
                    for cond in cond_list:
                        if cond in f[area_key]:
                            # Data shape: (trials, channels, time)
                            lfp_traces = f[area_key][cond][:]
                            # Average across channels for simplicity
                            avg_channel_traces = np.mean(lfp_traces, axis=1)
                            
                            for area in areas_in_key:
                                if area in TARGET_AREAS:
                                    all_lfp_data[area][group_name].extend(avg_channel_traces)
    return all_lfp_data

def calculate_and_plot_tfr(lfp_data):
    """Calculates and plots the Time-Frequency Response for each area and omission group."""
    
    for area in TARGET_AREAS:
        for group_name, trials in lfp_data[area].items():
            if not trials:
                print(f"  Skipping {area} - {group_name} due to no data.")
                continue

            print(f"  Calculating TFR for {area} - {group_name}...")
            
            all_trial_tfrs_db = []
            nperseg = 256
            noverlap = int(0.98 * nperseg)

            for trial_trace in trials:
                # Baseline calculation
                bl_start, bl_end = BASELINE_WINDOW
                f, _, Sxx_bl = spectrogram(trial_trace[bl_start:bl_end], fs=FS, window='hann', nperseg=nperseg, noverlap=noverlap)
                mean_bl_power = np.mean(Sxx_bl, axis=1)

                # TFR for the whole trace
                f, t, Sxx = spectrogram(trial_trace, fs=FS, window='hann', nperseg=nperseg, noverlap=noverlap)
                
                # dB conversion relative to baseline (avoid division by zero)
                Sxx_db = 10 * np.log10(Sxx / (mean_bl_power[:, np.newaxis] + 1e-12) + 1e-12)
                all_trial_tfrs_db.append(Sxx_db)

            # Average across all trials
            mean_tfr_db = np.mean(all_trial_tfrs_db, axis=0)
            
            # --- Plotting ---
            fig = go.Figure()
            
            # Convert time vector to ms from fixation onset (time 0 is sample 1000)
            time_ms = (t * 1000) - 1000

            fig.add_trace(go.Heatmap(
                z=mean_tfr_db,
                x=time_ms,
                y=f,
                colorscale='RdBu_r',
                zmid=0, # Center the colorscale at 0 dB change
                hovertemplate="Time: %{x:.0f}ms<br>Freq: %{y:.1f}Hz<br>Power: %{z:.2f}dB<extra></extra>"
            ))
            
            win_start, win_end = ANALYSIS_WINDOWS[group_name]
            fig.update_layout(
                title=f'LFP TFR for {area} during {group_name}',
                xaxis_title='Time from Fixation Onset (ms)',
                yaxis_title='Frequency (Hz)',
                template='plotly_white',
                xaxis_range=[win_start - 1000, win_end - 1000],
                yaxis_range=[1, 150] # Per user mandate
            )

            # Save files
            base_filename = f"{area}_{group_name}_tfr"
            html_path = os.path.join(OUTPUT_DIR, f"{base_filename}.html")
            svg_path = os.path.join(OUTPUT_DIR, f"{base_filename}.svg")
            fig.write_html(html_path)
            fig.write_image(svg_path)
            
            print(f"    ...saved {base_filename}")

if __name__ == '__main__':
    lfp_data = load_lfp_data()
    calculate_and_plot_tfr(lfp_data)
    print("\nFigure 5 generation complete.")
