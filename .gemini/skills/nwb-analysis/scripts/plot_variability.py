
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from pynwb import NWBHDF5IO
from collections import defaultdict
import re
from scipy.signal import medfilt
from scipy.signal.windows import gaussian

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128
CONDITIONS = {
    'RRRR': {'color': 'rgb(139, 69, 19)', 'fill': 'rgba(139, 69, 19, 0.2)', 'name': 'Standard (RRRR)'},
    'RXRR': {'color': 'rgb(255, 0, 0)', 'fill': 'rgba(255, 0, 0, 0.2)', 'name': 'Omit p2 (RXRR)'},
    'RRXR': {'color': 'rgb(0, 0, 255)', 'fill': 'rgba(0, 0, 255, 0.2)', 'name': 'Omit p3 (RRXR)'},
    'RRRX': {'color': 'rgb(0, 128, 0)', 'fill': 'rgba(0, 128, 0, 0.2)', 'name': 'Omit p4 (RRRX)'}
}

# Event window definitions for shading
EVENT_WINDOWS = {
    "fx": (0, 1000), "p1": (1000, 1531), "d1": (1531, 2031),
    "omit_p2": (2031, 2562), "omit_p3": (3062, 3593), "omit_p4": (4093, 4624)
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

def plot_final_variability():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    area_var_data = {area: {cond: [] for cond in CONDITIONS} for area in TARGET_AREAS}
    
    # Smoothing parameters
    kernel = gaussian(150, 30)
    kernel /= np.sum(kernel)
    med_kernel_size = 51

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Processing session {session_id} for Baselined Variability...")
        u_map = get_unit_to_area_map(nwb_path)
        
        for cond in CONDITIONS:
            spk_files = glob.glob(f'data/ses{session_id}-units-probe*-spk-{cond}.npy')
            for f in spk_files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                data = np.load(f, mmap_mode='r')
                for u_idx in range(data.shape[1]):
                    area = u_map.get((p_id, u_idx))
                    if area:
                        # 1. Compute time-resolved variance across trials
                        unit_var = np.var(data[:, u_idx, :], axis=0, ddof=1)
                        
                        # 2. Baselining to 0 during -500 to 0ms (indices 500:1000)
                        baseline = np.mean(unit_var[500:1000])
                        unit_var_aligned = unit_var - baseline
                        
                        # 3. Apply Filters
                        unit_var_med = medfilt(unit_var_aligned, kernel_size=med_kernel_size)
                        unit_var_smooth = np.convolve(unit_var_med, kernel, mode='same')
                        
                        area_var_data[area][cond].append(unit_var_smooth)

    time_axis = np.linspace(-1000, 5000, 6000)
    os.makedirs('figures/final_reports', exist_ok=True)

    for area in TARGET_AREAS:
        fig = go.Figure()
        
        # Add Event Shades
        shade_colors = {"fx": "rgba(100,100,100,0.05)", "p": "rgba(0,100,0,0.05)", "omit": "rgba(255,0,0,0.05)"}
        for event, (start, end) in EVENT_WINDOWS.items():
            color = shade_colors["omit"] if "omit" in event else shade_colors.get(event[:2], "rgba(0,0,0,0.05)")
            fig.add_vrect(x0=start-1000, x1=end-1000, fillcolor=color, line_width=0, annotation_text=event)

        for cond, cfg in CONDITIONS.items():
            traces = area_var_data[area][cond]
            if not traces: continue
            
            arr = np.array(traces)
            mean = np.mean(arr, axis=0)
            sem = np.std(arr, axis=0) / np.sqrt(len(traces))
            
            # Scale for visibility
            mean_scaled = mean * 1000
            sem_scaled = sem * 1000
            
            fig.add_trace(go.Scatter(x=time_axis, y=mean_scaled, mode='lines', line=dict(color=cfg['color']), name=cfg['name']))
            fig.add_trace(go.Scatter(x=np.concatenate([time_axis, time_axis[::-1]]), 
                                     y=np.concatenate([mean_scaled + sem_scaled, (mean_scaled - sem_scaled)[::-1]]),
                                     fill='toself', fillcolor=cfg['fill'], line=dict(color='rgba(255,255,255,0)'),
                                     hoverinfo="skip", showlegend=False))

        fig.update_layout(title=f"Neural Variability (Baselined -500-0ms): {area}", 
                          xaxis_title="Time (ms)", yaxis_title="ΔVariance (scaled)",
                          xaxis_range=[-750, 4124], template="plotly_white")
        
        output_name = f"FIG_03_Neural_Variability_{area}"
        fig.write_html(f"figures/final_reports/{output_name}.html")
        try: fig.write_image(f"figures/final_reports/{output_name}.svg")
        except: pass
        print(f"Saved baselined {area} variability plots as {output_name}.")

if __name__ == '__main__':
    plot_final_variability()
