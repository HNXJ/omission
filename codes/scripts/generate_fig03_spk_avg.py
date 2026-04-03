"""
generate_fig03_spk_avg.py
OMISSION 2026: Population Firing (FIG_03)
Grand average firing rates per area (11 areas).
V4 Refinement: White theme, pink omission patch, ±2SEM shading, triple export.
"""
import os
import glob
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data\arrays'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\oglo\fig_03_SPK_AVG_V4'
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONDITIONS = ['AAAB', 'AAAX', 'AAXB', 'AXAB', 'BBBA', 'BBBX', 'BBXA', 'BXBA', 'RRRR', 'RRRX', 'RRXR', 'RXRR']

# Omission timings (1000ms buffer included)
OMISSION_PATCHES = {
    'AXAB': (2031, 2562),
    'BXBA': (2031, 2562),
    'RXRR': (2031, 2562),
    'AAXB': (3062, 3593),
    'BBXA': (3062, 3593),
    'RRXR': (3062, 3593),
    'AAAX': (4093, 4624),
    'BBBX': (4093, 4624),
    'RRRX': (4093, 4624)
}

SESSION_AREAS = {
    '230831': {'0': 'FEF', '1': 'MT', '2': 'V4'},
    '230901': {'0': 'PFC', '1': 'MT', '2': 'V4'},
    '230720': {'0': 'V1', '1': 'V4'},
    '230629': {'0': 'V1', '1': 'V3'},
    '230630': {'0': 'PFC', '1': 'V4', '2': 'V1'},
    '230714': {'0': 'V1', '1': 'V3'},
    '230719': {'0': 'V1', '1': 'DP', '2': 'V3'},
    '230721': {'0': 'V1', '1': 'V3'},
    '230816': {'0': 'PFC', '1': 'V4', '2': 'V1'},
    '230818': {'0': 'PFC', '1': 'TEO', '2': 'MT'},
    '230823': {'0': 'FEF', '1': 'MT', '2': 'V1'},
    '230825': {'0': 'PFC', '1': 'MT', '2': 'V4'},
    '230830': {'0': 'PFC', '1': 'V4', '2': 'V1'}
}

# Targeted 11 Areas
TARGET_AREAS = ['V1', 'V2', 'V3', 'V4', 'MT', 'MST', 'TEO', 'FST', 'DP', 'PFC', 'FEF']

def simplify_area(name):
    name = name.replace(' ', '').upper()
    if 'V1' in name: return 'V1'
    if 'V2' in name: return 'V2'
    if 'V3' in name: return 'V3'
    if 'V4' in name: return 'V4'
    if 'MT' in name: return 'MT'
    if 'MST' in name: return 'MST'
    if 'TEO' in name: return 'TEO'
    if 'FST' in name: return 'FST'
    if 'DP' in name: return 'DP'
    if 'PFC' in name: return 'PFC'
    if 'FEF' in name: return 'FEF'
    return None

def smooth_fr(data, window_size=50):
    if len(data) < window_size: return data
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')

def run():
    print("Generating Figure 03: Population Firing V4...")
    
    for condition in CONDITIONS:
        print(f"  - Processing {condition}...")
        spike_files = glob.glob(os.path.join(DATA_DIR, f'ses*-units-probe*-spk-{condition}.npy'))
        
        area_data = {area: [] for area in TARGET_AREAS}
        sessions_processed = set()
        
        for f in spike_files:
            basename = os.path.basename(f)
            parts = basename.split('-')
            # Handle ses230831 style
            ses_str = parts[0].replace('ses', '')
            prb_str = parts[2].replace('probe', '')
            
            if ses_str in SESSION_AREAS and prb_str in SESSION_AREAS[ses_str]:
                area_key = SESSION_AREAS[ses_str][prb_str]
                simp_area = simplify_area(area_key)
                
                if simp_area is None or simp_area not in TARGET_AREAS:
                    continue
                
                try:
                    spikes = np.load(f, mmap_mode='r')
                    spikes = np.nan_to_num(spikes, nan=0.0, posinf=0.0, neginf=0.0)
                except Exception:
                    continue
                    
                sessions_processed.add(ses_str)
                
                # spikes shape: (n_trials, n_units, 6000)
                if spikes.shape[2] != 6000:
                    continue
                
                # Calculate firing rate (Hz) correctly: np.nanmean(spikes, axis=0) * 1000.0
                unit_avg_fr = np.nanmean(spikes, axis=0) * 1000.0 # (units, time)
                
                for u in range(unit_avg_fr.shape[0]):
                    area_data[simp_area].append(unit_avg_fr[u, :])
                    
        # Filter out areas with no data
        active_areas = [a for a in TARGET_AREAS if len(area_data[a]) > 0]
        
        if not active_areas:
            print(f"No valid spike data found for {condition}, skipping.")
            continue

        n_areas = len(active_areas)
        fig = make_subplots(rows=n_areas, cols=1, subplot_titles=active_areas, shared_xaxes=True, vertical_spacing=0.03)
        
        total_units = 0
        time_ax = np.arange(6000)
        
        for i, area in enumerate(active_areas):
            units_fr = np.array(area_data[area]) # (n_units, time)
            n_units = units_fr.shape[0]
            total_units += n_units
            
            mean_fr = np.nanmean(units_fr, axis=0)
            sem_fr = np.nanstd(units_fr, axis=0) / np.sqrt(max(1, n_units))
            
            # Smooth for visualization
            mean_fr_s = smooth_fr(mean_fr)
            sem_fr_s = smooth_fr(sem_fr)
            
            row_idx = i + 1
            
            # Plot 2-SEM Shading
            fig.add_trace(go.Scatter(
                x=np.concatenate([time_ax, time_ax[::-1]]),
                y=np.concatenate([mean_fr_s + 2*sem_fr_s, (mean_fr_s - 2*sem_fr_s)[::-1]]),
                fill='toself',
                fillcolor='rgba(128,128,128,0.3)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False
            ), row=row_idx, col=1)

            # Plot Mean
            fig.add_trace(go.Scatter(
                x=time_ax, y=mean_fr_s,
                mode='lines',
                line=dict(color='black', width=2),
                name=f"{area} Mean"
            ), row=row_idx, col=1)
            
            # Pink Omission Patch
            if condition in OMISSION_PATCHES:
                start, end = OMISSION_PATCHES[condition]
                fig.add_vrect(
                    x0=start, x1=end,
                    fillcolor="#FF1493", opacity=0.2,
                    layer="below", line_width=0,
                    row=row_idx, col=1
                )
                
        fig.update_layout(
            title=f"<b>Fig 03: Population Firing Rate across Areas ({condition})</b><br><sup>N = {total_units} total units | Mean ± 2SEM | Template: White</sup>",
            height=max(600, 250 * n_areas),
            template="plotly_white",
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time [ms]", row=n_areas, col=1)
        for i in range(n_areas):
            fig.update_yaxes(title_text="FR [Hz]", row=i+1, col=1)
            
        base_name = os.path.join(OUTPUT_DIR, f'fig_03_population_firing_{condition}')
        fig.write_html(base_name + '.html')
        fig.write_image(base_name + '.svg')
        fig.write_image(base_name + '.png')
        
        metadata = {
            "script": "generate_fig03_spk_avg.py",
            "condition": condition,
            "total_units": total_units,
            "areas": active_areas,
            "sessions_processed": list(sessions_processed),
            "omission_patch": OMISSION_PATCHES.get(condition, None)
        }
        with open(base_name + '.metadata.json', 'w') as f_meta:
            json.dump(metadata, f_meta, indent=4)
        
        print(f"Figure 03 generated for {condition}.")

if __name__ == '__main__':
    run()
