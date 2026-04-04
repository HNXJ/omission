
import numpy as np
import pandas as pd
import glob
import os
import sys
import plotly.graph_objects as go
from scipy.signal.windows import gaussian
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128

def get_unit_to_area_map(nwb_path):
    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            if nwbfile.units is None or nwbfile.electrodes is None: return {}
            
            units_df = nwbfile.units.to_dataframe()
            electrodes_df = nwbfile.electrodes.to_dataframe()
            
            # Group units by probe to assign local indices (0, 1, 2...)
            probe_units = defaultdict(list)
            
            for idx, unit in units_df.iterrows():
                peak_chan_id = int(float(unit['peak_channel_id']))
                if peak_chan_id not in electrodes_df.index: continue
                
                probe_id = int(peak_chan_id // CHANNELS_PER_PROBE)
                probe_units[probe_id].append((idx, peak_chan_id))

            for probe_id, units in probe_units.items():
                # Sort units by their NWB index to match .npy export order
                units.sort(key=lambda x: x[0])
                
                for local_idx, (global_idx, peak_chan_id) in enumerate(units):
                    elec = electrodes_df.loc[peak_chan_id]
                    raw_label = elec.get('location', elec.get('label', 'unknown'))
                    if isinstance(raw_label, bytes): raw_label = raw_label.decode('utf-8')
                    
                    clean_label = raw_label.replace('/', ',')
                    raw_areas = [a.strip() for a in clean_label.split(',')]
                    mapped_areas = []
                    for a in raw_areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped_areas.extend(m)
                        else: mapped_areas.append(m)
                    
                    num_areas = len(mapped_areas)
                    channel_in_probe = peak_chan_id % CHANNELS_PER_PROBE
                    segment_width = CHANNELS_PER_PROBE / num_areas
                    area_index = min(int(channel_in_probe // segment_width), num_areas - 1)
                    assigned_area = mapped_areas[area_index]
                    
                    if assigned_area in TARGET_AREAS:
                        unit_map[(probe_id, local_idx)] = assigned_area
    except: pass
    return unit_map

def plot_area_firing():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    area_data_accumulator = {area: [] for area in TARGET_AREAS}
    kernel = gaussian(100, 20)
    kernel /= np.sum(kernel)

    print(f"Processing {len(nwb_files)} sessions...")

    for nwb_path in nwb_files:
        match = re.search(r'ses-(\d+)', nwb_path)
        if not match: continue
        session_id = match.group(1)
        
        unit_to_area = get_unit_to_area_map(nwb_path)
        if not unit_to_area: continue

        spk_files = glob.glob(f'data/ses{session_id}-units-probe*-spk-RRRR.npy')
        
        if not spk_files: continue

        print(f"  - Session {session_id}: processing {len(spk_files)} probe files...")
        session_assigned_counts = defaultdict(int)

        for f in spk_files:
            try:
                probe_match = re.search(r'probe(\d+)', f)
                if not probe_match: continue
                probe_id = int(probe_match.group(1))
                
                data = np.load(f, mmap_mode='r')
                
                for unit_idx in range(data.shape[1]):
                    area = unit_to_area.get((probe_id, unit_idx))
                    if area:
                        unit_spikes = data[:, unit_idx, :]
                        mean_spikes = np.mean(unit_spikes, axis=0)
                        smoothed = np.convolve(mean_spikes, kernel, mode='same') * 1000
                        area_data_accumulator[area].append(smoothed)
                        session_assigned_counts[area] += 1
            except Exception as e:
                print(f"    -> ERROR loading file {f}: {e}")
        
        print(f"    - Session {session_id} Assignments: {dict(session_assigned_counts)}")

    time_axis = np.linspace(-1000, 5000, 6000)
    # Standardized Event Shading
    EVENTS = {
        "fx": (-1000, 0, 'rgba(128,128,128,0.1)'),
        "p1": (0, 531, 'rgba(128,128,128,0.15)'),
        "d1": (531, 1031, 'rgba(128,128,128,0.1)'),
        "p2": (1031, 1562, 'rgba(255,0,0,0.12)'),
        "d2": (1562, 2062, 'rgba(128,128,128,0.1)'),
        "p3": (2062, 2593, 'rgba(0,0,255,0.12)'),
        "d3": (2593, 3093, 'rgba(128,128,128,0.1)'),
        "p4": (3093, 3624, 'rgba(0,128,0,0.12)'),
        "d4": (3624, 4124, 'rgba(128,128,128,0.1)')
    }

    os.makedirs('figures/final_reports', exist_ok=True)

    for area in TARGET_AREAS:
        all_unit_rates = area_data_accumulator[area]
        if not all_unit_rates:
            continue
        
        avg_rate = np.mean(all_unit_rates, axis=0)
        sem_rate = np.std(all_unit_rates, axis=0) / np.sqrt(len(all_unit_rates))
        
        fig = go.Figure()
        
        # Add Standard Shades
        for name, (start, end, color) in EVENTS.items():
            fig.add_vrect(x0=start, x1=end, fillcolor=color, line_width=0, 
                          annotation_text=name, annotation_position="top left")

        # Plot Average + SEM
        fig.add_trace(go.Scatter(x=time_axis, y=avg_rate + sem_rate, mode='lines', 
                                 line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=time_axis, y=avg_rate - sem_rate, mode='lines', 
                                 line=dict(width=0), fill='tonexty', 
                                 fillcolor='rgba(139, 69, 19, 0.2)', showlegend=False))
        fig.add_trace(go.Scatter(x=time_axis, y=avg_rate, mode='lines', 
                                 line=dict(color='rgb(139, 69, 19)'), name=f'{area} Avg (RRRR)'))

        fig.update_layout(title=f"Grand Average Firing Rate: {area} (n={len(all_unit_rates)})",
                          xaxis_title="Time (ms)", yaxis_title="Firing Rate (Hz)",
                          xaxis_range=[-750, 4124], template="plotly_white")
        fig.write_html(f"figures/final_reports/FIG_01_FiringRate_{area}.html")

if __name__ == '__main__':
    plot_area_firing()
