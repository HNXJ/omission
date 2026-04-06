
import numpy as np
import pandas as pd
import glob
import os
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal.windows import gaussian
from scipy.stats import ttest_ind
from sklearn.cluster import KMeans
from pynwb import NWBHDF5IO
import plotly.colors

# --- Constants ---
OUTPUT_DIR = 'figures/oglo/fig_04_SPK_5_group_kmeans_ALLSESSIONS'
os.makedirs(OUTPUT_DIR, exist_ok=True)
CONDITION = 'RRRX'
N_CLUSTERS = 5

TARGET_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128
UNIT_MAP_CACHE = {}

# Time windows relative to fixation onset (0 ms)
WINDOWS = {
    'p1': (1000, 1531),
    'd1': (1531, 2031),
    'd2-p3-d3': (2562, 4093),
    'd3-p4-d4': (3593, 5124)
}

def get_unit_to_area_map(nwb_path):
    if nwb_path in UNIT_MAP_CACHE: return UNIT_MAP_CACHE[nwb_path]
    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            elec_df = nwbfile.electrodes.to_dataframe()
            for unit_id, unit_row in units_df.iterrows():
                peak_channel_id = int(float(unit_row['peak_channel_id']))
                electrode = elec_df.loc[peak_channel_id]
                location_str = electrode.get('location', 'unknown').decode('utf-8') if isinstance(electrode.get('location', 'unknown'), bytes) else electrode.get('location', 'unknown')
                area = location_str.split('/')[0].split(',')[0].strip()
                if area in TARGET_AREAS: unit_map[unit_id] = area
    except Exception as e: print(f"  NWB warning: {e}")
    UNIT_MAP_CACHE[nwb_path] = unit_map
    return unit_map

def load_rrrx_spiking_data():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    all_units_data = []
    
    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Processing session {session_id} for {CONDITION} data...")
        unit_to_area = get_unit_to_area_map(nwb_path)
        
        spk_files = glob.glob(f'data/ses{session_id}-units-*-spk-{CONDITION}.npy')
        for f in spk_files:
            try:
                data = np.load(f) # (trials, units, time)
                if data.ndim != 3: continue
                probe_id = int(re.search(r'probe(\d+)', f).group(1))

                with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                    nwbfile = io.read()
                    probe_unit_ids = [uid for uid, urow in nwbfile.units.to_dataframe().iterrows() if (int(float(urow['peak_channel_id'])) // CHANNELS_PER_PROBE) == probe_id]

                for i, unit_id in enumerate(probe_unit_ids):
                    if i < data.shape[1]:
                        area = unit_to_area.get(unit_id)
                        if area:
                            all_units_data.append({
                                'unit_id': f"{session_id}_{probe_id}_{unit_id}",
                                'area': area,
                                'traces': data[:, i, :] # Keep all trials
                            })
            except Exception as e: print(f"  File warning: {e}")
    return all_units_data

def perform_task_responsive_analysis(all_units):
    print("\n--- Performing Task-Responsive Analysis ---")
    responsive_count = 0
    total_units = len(all_units)
    
    p1_start, p1_end = WINDOWS['p1']
    d1_start, d1_end = WINDOWS['d1']

    for unit in all_units:
        p1_traces = unit['traces'][:, p1_start:p1_end].mean(axis=1) * 1000
        d1_traces = unit['traces'][:, d1_start:d1_end].mean(axis=1) * 1000
        
        mean_p1 = np.mean(p1_traces)
        mean_d1 = np.mean(d1_traces)
        
        if mean_d1 > 0 and mean_p1 > (mean_d1 * 1.1):
            stat, p_val = ttest_ind(p1_traces, d1_traces, equal_var=False, nan_policy='omit')
            if p_val < 0.05:
                responsive_count += 1
    
    print(f"Found {responsive_count} / {total_units} 'task-responsive' units (p<0.05 and >10% increase from d1 to p1).")
    return responsive_count

def cluster_and_plot(all_units, window_name):
    print(f"\n--- Clustering for window: {window_name} ---")
    start, end = WINDOWS[window_name]
    
    # Prepare data for clustering: mean trace over the window for each unit
    feature_vectors = [np.mean(unit['traces'][:, start:end], axis=0) for unit in all_units]
    
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    labels = kmeans.fit_predict(feature_vectors)
    
    # Plotting
    fig = make_subplots(rows=N_CLUSTERS, cols=1, shared_xaxes=True, subplot_titles=[f"Cluster {i+1}" for i in range(N_CLUSTERS)])
    time_axis = np.arange(end - start)
    
    for i in range(N_CLUSTERS):
        cluster_indices = np.where(labels == i)[0]
        if len(cluster_indices) == 0: continue
        
        cluster_traces = np.array([feature_vectors[j] for j in cluster_indices])
        mean_trace = np.mean(cluster_traces, axis=0)
        sem_trace = np.std(cluster_traces, axis=0) / np.sqrt(len(cluster_indices))
        
        fig.add_trace(go.Scatter(x=time_axis, y=mean_trace, mode='lines', name=f'Mean (N={len(cluster_indices)})'), row=i+1, col=1)
        fig.add_trace(go.Scatter(x=np.concatenate([time_axis, time_axis[::-1]]), y=np.concatenate([mean_trace - sem_trace, (mean_trace + sem_trace)[::-1]]), fill='toself', opacity=0.3, line=dict(color='rgba(255,255,255,0)'), showlegend=False), row=i+1, col=1)
        
    fig.update_layout(
        title=f'K-Means Clusters ({N_CLUSTERS} groups) for {CONDITION} in window: {window_name}',
        height=300 * N_CLUSTERS,
        template='plotly_white'
    )
    fig.update_xaxes(title_text='Time in window (ms)', row=N_CLUSTERS, col=1)

    base_filename = f"{CONDITION}_{window_name.replace('-', '_')}_kmeans"
    html_path = os.path.join(OUTPUT_DIR, f"{base_filename}.html")
    svg_path = os.path.join(OUTPUT_DIR, f"{base_filename}.svg")
    fig.write_html(html_path)
    fig.write_image(svg_path)
    print(f"Saved {base_filename}")

if __name__ == '__main__':
    all_units = load_rrrx_spiking_data()
    if all_units:
        perform_task_responsive_analysis(all_units)
        cluster_and_plot(all_units, 'd2-p3-d3')
        cluster_and_plot(all_units, 'd3-p4-d4')
        print("\nFigure 4 generation complete.")
    else:
        print("No units found to process.")
