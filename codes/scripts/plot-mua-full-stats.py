
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from scipy.signal.windows import gaussian
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128
CONDITIONS = {
    'RRRR': {'color': 'rgb(139, 69, 19)', 'fill': 'rgba(139, 69, 19, 0.2)', 'name': 'Standard (RRRR)'},
    'RXRR': {'color': 'rgb(255, 0, 0)', 'fill': 'rgba(255, 0, 0, 0.2)', 'name': 'Omit p2 (RXRR)'},
    'RRXR': {'color': 'rgb(0, 0, 255)', 'fill': 'rgba(0, 0, 255, 0.2)', 'name': 'Omit p3 (RRXR)'},
    'RRRX': {'color': 'rgb(0, 128, 0)', 'fill': 'rgba(0, 128, 0, 0.2)', 'name': 'Omit p4 (RRRX)'}
}

def get_unit_to_area_map(nwb_path):
    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            elec_df = nwbfile.electrodes.to_dataframe()
            probe_units = defaultdict(list)
            for idx, unit in units_df.iterrows():
                p_id = int(float(unit['peak_channel_id']))
                probe_id = p_id // CHANNELS_PER_PROBE
                probe_units[probe_id].append((idx, p_id))
            for probe_id, units in probe_units.items():
                units.sort(key=lambda x: x[0])
                for local_idx, (global_idx, p_id) in enumerate(units):
                    elec = elec_df.loc[p_id]
                    raw = elec.get('location', elec.get('label', 'unknown'))
                    if isinstance(raw, bytes): raw = raw.decode('utf-8')
                    clean = raw.replace('/', ',')
                    raw_areas = [a.strip() for a in clean.split(',')]
                    mapped = []
                    for a in raw_areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped.extend(m)
                        else: mapped.append(m)
                    sw = CHANNELS_PER_PROBE / len(mapped)
                    area = mapped[min(int((p_id % CHANNELS_PER_PROBE) // sw), len(mapped)-1)]
                    if area in TARGET_AREAS: unit_map[(probe_id, local_idx)] = area
    except: pass
    return unit_map

def plot_final_mua():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    area_data = {area: {cond: [] for cond in CONDITIONS} for area in TARGET_AREAS}
    
    kernel = gaussian(100, 20)
    kernel /= np.sum(kernel)

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Processing session {session_id} for MUA...")
        u_map = get_unit_to_area_map(nwb_path)
        
        for cond in CONDITIONS:
            spk_files = glob.glob(f'data/ses{session_id}-units-probe*-spk-{cond}.npy')
            # Group data by area for this session to sum across channels
            session_area_spks = defaultdict(list)
            for f in spk_files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                data = np.load(f, mmap_mode='r')
                for u_idx in range(data.shape[1]):
                    area = u_map.get((p_id, u_idx))
                    if area: session_area_spks[area].append(data[:, u_idx, :])
            
            for area, spikes_list in session_area_spks.items():
                # MUA: sum all spikes across units in the same area/probe
                # Shape: (trials, time)
                mua_sum = np.sum(spikes_list, axis=0) * 1000 / len(spikes_list) # Average per unit for normalized MUA
                smoothed = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='same'), axis=1, arr=mua_sum)
                # Append trials individually to area_data for SEM calculation
                for t_idx in range(smoothed.shape[0]):
                    area_data[area][cond].append(smoothed[t_idx, :])

    time_axis = np.linspace(-1000, 5000, 6000)
    os.makedirs('figures/final_reports', exist_ok=True)

    # Standardized Event Shading
    EVENTS = {
        "fx": (0, 1000, 'rgba(128,128,128,0.08)'),
        "p1": (1000, 1531, 'rgba(128,128,128,0.12)'),
        "d1": (1531, 2031, 'rgba(128,128,128,0.08)'),
        "p2": (2031, 2562, 'rgba(255,0,0,0.12)'),   # Red for RXRR
        "d2": (2562, 3062, 'rgba(128,128,128,0.08)'),
        "p3": (3062, 3593, 'rgba(0,0,255,0.12)'),   # Blue for RRXR
        "d3": (3593, 4093, 'rgba(128,128,128,0.08)'),
        "p4": (4093, 4624, 'rgba(0,128,0,0.12)'),   # Green for RRRX
        "d4": (4624, 5124, 'rgba(128,128,128,0.08)')
    }

    for area in TARGET_AREAS:
        fig = go.Figure()
        
        # Add Event Shades and Labels
        for name, (start, end, color) in EVENTS.items():
            fig.add_vrect(x0=start-1000, x1=end-1000, fillcolor=color, line_width=0, 
                          annotation_text=name, annotation_position="top left")

        for cond, cfg in CONDITIONS.items():
            trials = area_data[area][cond]
            if not trials: continue
            
            arr = np.array(trials)
            mean = np.mean(arr, axis=0)
            sem = np.std(arr, axis=0) / np.sqrt(len(trials))
            
            fig.add_trace(go.Scatter(x=time_axis, y=mean, mode='lines', line=dict(color=cfg['color']), name=cfg['name']))
            fig.add_trace(go.Scatter(x=np.concatenate([time_axis, time_axis[::-1]]), 
                                     y=np.concatenate([mean + sem, (mean - sem)[::-1]]),
                                     fill='toself', fillcolor=cfg['fill'], line=dict(color='rgba(255,255,255,0)'),
                                     hoverinfo="skip", showlegend=False))

        fig.update_layout(title=f"Average Multi-Unit Activity (MUA): {area}", 
                          xaxis_title="Time (ms)", yaxis_title="Firing Rate (Hz)",
                          xaxis_range=[-750, 4124], template="plotly_white")
        
        output_name = f"FIG_02_MUA_Activity_{area}"
        fig.write_html(f"figures/final_reports/{output_name}.html")
        try: fig.write_image(f"figures/final_reports/{output_name}.svg")
        except: pass
        print(f"Saved {area} MUA plots as {output_name}.")

if __name__ == '__main__':
    plot_final_mua()
