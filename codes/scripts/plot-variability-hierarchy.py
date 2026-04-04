
import numpy as np
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from pynwb import NWBHDF5IO
from collections import defaultdict
import re

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128
AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}

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
                    if area in AREA_ORDER: unit_map[(probe_id, local_idx)] = area
    except: pass
    return unit_map

def plot_variability_hierarchy():
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    
    # 1. Variability during Omission (Omit window)
    # Area -> list of values
    omit_variability = {area: [] for area in AREA_ORDER}
    
    # 2. Post-Omission Scaling
    # Area -> {'standard': [], 'post_omit': []}
    post_omit_data = {area: {'std': [], 'po': []} for area in AREA_ORDER}

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Analyzing variability hierarchy for session {session_id}...")
        u_map = get_unit_to_area_map(nwb_path)
        
        # Load conditions: RRRR (std), RXRR (omit p2), RRXR (omit p3), RRRX (omit p4)
        cond_files = {}
        for c in ['RRRR', 'RXRR', 'RRXR', 'RRRX']:
            cond_files[c] = glob.glob(f'data/ses{session_id}-units-probe*-spk-{c}.npy')

        for (probe_id, local_idx), area in u_map.items():
            # Extract baselined variability
            def get_aligned_var(cond, start, end):
                f = next((f for f in cond_files[cond] if f"probe{probe_id}" in f), None)
                if not f: return None
                data = np.load(f, mmap_mode='r')[:, local_idx, :]
                unit_var = np.var(data, axis=0, ddof=1)
                baseline = np.mean(unit_var[500:1000]) # -500 to 0ms
                return np.mean(unit_var[start:end] - baseline)

            # A. Omission Variability (Average p2, p3, p4 from corresponding omit trials)
            v_p2 = get_aligned_var('RXRR', 2031, 2562)
            v_p3 = get_aligned_var('RRXR', 3062, 3593)
            v_p4 = get_aligned_var('RRRX', 4093, 4624)
            
            vals = [v for v in [v_p2, v_p3, v_p4] if v is not None]
            if vals: omit_variability[area].append(np.mean(vals))

            # B. Post-Omission Scaling
            # Case 1: RXRR Omit p2 -> Analyze p3 (3062:3593)
            # Case 2: RRXR Omit p3 -> Analyze p4 (4093:4624)
            
            # Post-Omit values
            po_p3 = get_aligned_var('RXRR', 3062, 3593)
            po_p4 = get_aligned_var('RRXR', 4093, 4624)
            
            # Standard equivalents from RRRR
            std_p3 = get_aligned_var('RRRR', 3062, 3593)
            std_p4 = get_aligned_var('RRRR', 4093, 4624)
            
            if po_p3 is not None and std_p3 is not None:
                post_omit_data[area]['po'].append(po_p3)
                post_omit_data[area]['std'].append(std_p3)
            if po_p4 is not None and std_p4 is not None:
                post_omit_data[area]['po'].append(po_p4)
                post_omit_data[area]['std'].append(std_p4)

    os.makedirs('figures/final_reports', exist_ok=True)

    # FIGURE 4A: Omission Variability Hierarchy (Bar)
    means = [np.mean(omit_variability[a]) if omit_variability[a] else 0 for a in AREA_ORDER]
    sems = [np.std(omit_variability[a])/np.sqrt(len(omit_variability[a])) if omit_variability[a] else 0 for a in AREA_ORDER]
    
    fig_a = go.Figure(data=[go.Bar(x=AREA_ORDER, y=means, error_y=dict(type='data', array=sems),
                                  marker_color='indianred')])
    fig_a.update_layout(title="Neural Variability Hierarchy during Omission",
                        xaxis_title="Brain Area (Hierarchy)", yaxis_title="ΔVariance (Baselined)",
                        template="plotly_white")
    fig_a.write_html("figures/final_reports/FIG_04A_Variability_Hierarchy.html")
    try: fig_a.write_image("figures/final_reports/FIG_04A_Variability_Hierarchy.svg")
    except: pass

    # FIGURE 4B: Post-Omission Scaling (Comparison Bar)
    std_means = [np.mean(post_omit_data[a]['std']) if post_omit_data[a]['std'] else 0 for a in AREA_ORDER]
    po_means = [np.mean(post_omit_data[a]['po']) if post_omit_data[a]['po'] else 0 for a in AREA_ORDER]
    
    fig_b = go.Figure(data=[
        go.Bar(name='Standard Stimulus', x=AREA_ORDER, y=std_means),
        go.Bar(name='Post-Omission Stimulus', x=AREA_ORDER, y=po_means)
    ])
    fig_b.update_layout(barmode='group', title="Post-Omission Variability Scaling",
                        xaxis_title="Brain Area", yaxis_title="ΔVariance (Baselined)",
                        template="plotly_white")
    fig_b.write_html("figures/final_reports/FIG_04B_Post_Omission_Scaling.html")
    try: fig_b.write_image("figures/final_reports/FIG_04B_Post_Omission_Scaling.svg")
    except: pass

    print("Saved Figure 4A and 4B to figures/final_reports/")

if __name__ == '__main__':
    plot_variability_hierarchy()
