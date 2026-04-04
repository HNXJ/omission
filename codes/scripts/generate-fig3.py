
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from scipy.signal.windows import gaussian
from pynwb import NWBHDF5IO
from collections import defaultdict
import re
import plotly.colors

# --- Constants ---
OUTPUT_DIR = 'figures/oglo/fig_03_SPK_Firing_ALLSESSIONS'
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128

ALL_CONDITIONS = [
    'AAAB', 'AXAB', 'AAXB', 'AAAX',
    'BBBA', 'BXBA', 'BBXA', 'BBBX',
    'RRRR', 'RXRR', 'RRXR', 'RRRX'
]

# Generate a color palette for all areas
AREA_COLORS = plotly.colors.qualitative.Plotly
COLOR_MAP = {area: AREA_COLORS[i % len(AREA_COLORS)] for i, area in enumerate(TARGET_AREAS)}

# Cached unit map to speed up processing
UNIT_MAP_CACHE = {}

def get_unit_to_area_map(nwb_path):
    """Maps unit IDs to brain areas using NWB metadata, with caching."""
    if nwb_path in UNIT_MAP_CACHE:
        return UNIT_MAP_CACHE[nwb_path]

    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            elec_df = nwbfile.electrodes.to_dataframe()
            
            for unit_id, unit_row in units_df.iterrows():
                # Find the electrode for this unit using the peak_channel_id
                peak_channel_id = int(float(unit_row['peak_channel_id']))
                electrode = elec_df.loc[peak_channel_id]
                # Location is often a string like 'V1/V2'
                location_str = electrode.get('location', 'unknown')
                if isinstance(location_str, bytes):
                    location_str = location_str.decode('utf-8')
                
                # Take the first area listed if multiple
                area = location_str.split('/')[0].split(',')[0].strip()

                if area in TARGET_AREAS:
                    unit_map[unit_id] = area
    except Exception as e:
        print(f"  Warning: Could not process NWB file {nwb_path}: {e}")
        pass
    
    UNIT_MAP_CACHE[nwb_path] = unit_map
    return unit_map

def load_all_spiking_data():
    """
    Loads all spiking data from .npy files and aggregates it by condition and area.
    Returns a dictionary: data[condition][area] = list of trial-averaged firing rates.
    """
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    area_data = {cond: {area: [] for area in TARGET_AREAS} for cond in ALL_CONDITIONS}
    
    kernel = gaussian(100, 20)
    kernel /= np.sum(kernel)

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Processing session {session_id}...")
        unit_to_area = get_unit_to_area_map(nwb_path)

        for cond in ALL_CONDITIONS:
            spk_files = glob.glob(f'data/ses{session_id}-units-*-spk-{cond}.npy')
            for f in spk_files:
                try:
                    # Shape of data: (n_trials, n_units, n_timepoints)
                    data = np.load(f, mmap_mode='r')
                    if data.ndim != 3 or data.shape[0] == 0:
                        continue
                    
                    # Get the unit IDs from the nwb file based on probe
                    probe_id = int(re.search(r'probe(\d+)', f).group(1))

                    # This part is tricky as npy files don't store unit IDs.
                    # We assume the order of units in the npy file matches the order in the NWB file for that probe.
                    # This is a strong assumption but often holds.
                    
                    with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                         nwbfile = io.read()
                         probe_unit_ids = [uid for uid, urow in nwbfile.units.to_dataframe().iterrows() if (int(float(urow['peak_channel_id'])) // CHANNELS_PER_PROBE) == probe_id]

                    for i, unit_id in enumerate(probe_unit_ids):
                         if i < data.shape[1]:
                            area = unit_to_area.get(unit_id)
                            if area:
                                unit_mean_fr = np.mean(data[:, i, :], axis=0) * 1000  # Convert to Hz
                                smoothed_fr = np.convolve(unit_mean_fr, kernel, mode='same')
                                area_data[cond][area].append(smoothed_fr)
                except Exception as e:
                    # print(f"  Could not process file {f}: {e}")
                    pass
    return area_data

def plot_firing_rates_by_condition(data):
    """Generates one plot per condition, showing all area traces."""
    time_axis = np.linspace(-1000, 5000, 6000)

    for condition in ALL_CONDITIONS:
        print(f"  Plotting for condition: {condition}...")
        fig = go.Figure()
        
        caption_stats = f"<b>Spike Rate (Hz) Statistics for Condition: {condition}</b><br>"
        
        for area in TARGET_AREAS:
            traces = data[condition][area]
            if not traces:
                continue

            n_units = len(traces)
            trace_array = np.array(traces)
            
            mean_trace = np.mean(trace_array, axis=0)
            sem_trace = np.std(trace_array, axis=0) / np.sqrt(n_units)
            
            # Add trace for the area
            fig.add_trace(go.Scatter(
                x=time_axis, y=mean_trace,
                name=area, line=dict(color=COLOR_MAP[area]),
                legendgroup=area
            ))
            # Add SEM shade
            fig.add_trace(go.Scatter(
                x=np.concatenate([time_axis, time_axis[::-1]]),
                y=np.concatenate([mean_trace - sem_trace, (mean_trace + sem_trace)[::-1]]),
                fill='toself', fillcolor=COLOR_MAP[area], opacity=0.2,
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip", showlegend=False, legendgroup=area
            ))

            caption_stats += f"{area} (N={n_units} units): Peak={np.max(mean_trace):.2f} Hz, Mean={np.mean(mean_trace):.2f} Hz<br>"

        fig.update_layout(
            title=f"Average Single-Unit Firing Rates: Condition {condition}",
            xaxis_title="Time from Fixation Onset (ms)",
            yaxis_title="Firing Rate (Hz)",
            template="plotly_white",
            height=700,
            width=1400,
            annotations=[
                dict(
                    text=caption_stats,
                    showarrow=False,
                    xref='paper', yref='paper',
                    x=0.5, y=-0.3,
                    align='center'
                )
            ],
            margin=dict(b=200)
        )
        
        # Save files
        base_filename = f"{condition}_all_areas_firing_rate"
        html_path = os.path.join(OUTPUT_DIR, f"{base_filename}.html")
        svg_path = os.path.join(OUTPUT_DIR, f"{base_filename}.svg")

        fig.write_html(html_path)
        fig.write_image(svg_path)

    print("All condition plots saved.")

if __name__ == '__main__':
    spiking_data = load_all_spiking_data()
    plot_firing_rates_by_condition(spiking_data)
    print("Figure 3 generation complete.")
