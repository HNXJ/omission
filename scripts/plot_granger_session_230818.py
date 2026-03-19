
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import nitime.analysis as na
import nitime.timeseries as ts
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
CHANNELS_PER_PROBE = 128
SESSION_ID = '230818'
TARGET_AREAS = ['PFC', 'MT', 'MST']
SAMPLING_RATE = 1000.0
ORDER = 15

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

def plot_complex_granger():
    nwb_path = glob.glob(f'data/sub-*_ses-{SESSION_ID}_rec.nwb')[0]
    u_map = get_unit_to_area_map(nwb_path)
    
    # Aggregate average spiking for each area
    # Condition: RRRR (Standard)
    area_averages = {area: [] for area in TARGET_AREAS}
    spk_files = glob.glob(f'data/ses{SESSION_ID}-units-probe*-spk-RRRR.npy')
    
    for f in spk_files:
        p_id = int(re.search(r'probe(\d+)', f).group(1))
        data = np.load(f, mmap_mode='r')
        for u_idx in range(data.shape[1]):
            area = u_map.get((p_id, u_idx))
            if area in TARGET_AREAS:
                area_averages[area].append(np.mean(data[:, u_idx, :], axis=0) * 1000)
    
    # Compute population average per area
    # Shape: (3, 6000)
    signals = np.stack([np.mean(area_averages[a], axis=0) for area in TARGET_AREAS for a in [area]])
    
    # Granger Analysis (nitime)
    tseries = ts.TimeSeries(signals, sampling_rate=SAMPLING_RATE)
    g_analyzer = na.GrangerAnalyzer(tseries, order=ORDER)
    freqs = g_analyzer.frequencies
    
    # Setup Figure (4 subplots)
    fig = make_subplots(
        rows=2, cols=2, 
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]],
        subplot_titles=("Spectral Causality: PFC-MT", "Spectral Causality: PFC-MST", 
                        "Spectral Causality: MT-MST", "Connectivity Schematic")
    )

    # PFC (0), MT (1), MST (2)
    # PFC <-> MT
    fig.add_trace(go.Scatter(x=freqs, y=g_analyzer.causality_xy[1, 0, :], name='PFC -> MT'), row=1, col=1)
    fig.add_trace(go.Scatter(x=freqs, y=g_analyzer.causality_yx[0, 1, :], name='MT -> PFC'), row=1, col=1)
    
    # PFC <-> MST
    fig.add_trace(go.Scatter(x=freqs, y=g_analyzer.causality_xy[2, 0, :], name='PFC -> MST'), row=1, col=2)
    fig.add_trace(go.Scatter(x=freqs, y=g_analyzer.causality_yx[0, 2, :], name='MST -> PFC'), row=1, col=2)
    
    # MT <-> MST
    fig.add_trace(go.Scatter(x=freqs, y=g_analyzer.causality_xy[2, 1, :], name='MT -> MST'), row=2, col=1)
    fig.add_trace(go.Scatter(x=freqs, y=g_analyzer.causality_yx[1, 2, :], name='MST -> MT'), row=2, col=1)

    # Simplified Schematic (Subplot 4)
    fig.add_trace(go.Scatter(x=[0, 1, 0.5], y=[1, 1, 0], mode='markers+text', 
                             text=['PFC', 'MT', 'MST'], textposition="top center",
                             marker=dict(size=40, color=['red', 'blue', 'green'])), row=2, col=2)

    fig.update_layout(title=f"Complex Granger Causality: Session {SESSION_ID} (Standard)", 
                      xaxis_range=[0, 100], template="plotly_white", height=800)
    
    os.makedirs('figures/final_reports', exist_ok=True)
    fig.write_html(f"figures/final_reports/ses-{SESSION_ID}_complex_granger.html")
    try: fig.write_image(f"figures/final_reports/ses-{SESSION_ID}_complex_granger.svg")
    except: pass
    print(f"Saved complex Granger plot for session {SESSION_ID}.")

if __name__ == '__main__':
    plot_complex_granger()
