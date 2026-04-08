
import numpy as np
import pandas as pd
import glob
import os
from pynwb import NWBHDF5IO
from collections import defaultdict
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import plotly.graph_objects as go
from codes.config.paths import DATA_DIR, FIGURES_DIR

AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
CHANNELS_PER_PROBE = 128
AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
COND_IDENTITY = ['AAAX', 'BBBX', 'RRRX']
LABEL_MAP = {'AAAX': 0, 'BBBX': 1, 'RRRX': 2}

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
    except Exception as e:
        print(f"Error processing {nwb_path}: {e}")
    return unit_map

def decode_figure_5():
    nwb_files = glob.glob(str(DATA_DIR / 'sub-*_ses-*_rec.nwb'))
    
    # Session -> Area -> {'X': [], 'y': []}
    session_results = []
    behavior_all = {'X': [], 'y': []}

    for nwb_path in nwb_files:
        session_id = re.search(r'ses-(\d+)', nwb_path).group(1)
        print(f"Loading data for session {session_id}...")
        u_map = get_unit_to_area_map(nwb_path)
        
        # Identity Decoding per Session
        session_area_data = {area: {'X': [], 'y': []} for area in AREA_ORDER}
        
        for c in COND_IDENTITY:
            spk_files = glob.glob(str(DATA_DIR / f'ses{session_id}-units-probe*-spk-{c}.npy'))
            probe_data = {}
            for f in spk_files:
                p_id = int(re.search(r'probe(\d+)', f).group(1))
                probe_data[p_id] = np.load(f, mmap_mode='r')
            
            if not probe_data: continue
            
            num_trials = probe_data[list(probe_data.keys())[0]].shape[0]
            for t_idx in range(num_trials):
                area_vecs = {area: [] for area in AREA_ORDER}
                for (p_id, u_idx), area in u_map.items():
                    if p_id in probe_data:
                        fr = np.mean(probe_data[p_id][t_idx, u_idx, 4093:4624]) * 1000
                        area_vecs[area].append(fr)
                
                for area, vec in area_vecs.items():
                    if vec:
                        session_area_data[area]['X'].append(vec)
                        session_area_data[area]['y'].append(LABEL_MAP[c])

        # Run Decoding for this session
        for area in AREA_ORDER:
            X = np.array(session_area_data[area]['X'])
            y = np.array(session_area_data[area]['y'])
            if len(y) > 15 and len(np.unique(y)) >= 2:
                try:
                    # 50-50 split and shuffled (random_state=None or 42 with shuffle=True)
                    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.50, random_state=None, shuffle=True, stratify=y)
                    scaler = StandardScaler()
                    X_tr = scaler.fit_transform(X_tr); X_te = scaler.transform(X_te)
                    # Ternary decoding (A vs B vs R)
                    clf = LogisticRegression(max_iter=1000, multi_class='multinomial').fit(X_tr, y_tr)
                    session_results.append({
                        'session': session_id, 'Area': area, 
                        'Train': accuracy_score(y_tr, clf.predict(X_tr)),
                        'Test': accuracy_score(y_te, clf.predict(X_te))
                    })
                except Exception as e:
                    print(f"Error decoding {area} in {session_id}: {e}")

        # Behavioral (Aggregate across sessions)
        f_beh = glob.glob(str(DATA_DIR / f'ses{session_id}-behavioral-AAAX.npy'))
        if f_beh:
            beh_data = np.load(f_beh[0])
            for t_idx in range(beh_data.shape[0]):
                def extract_kinematics(x, y):
                    vx = np.diff(x); vy = np.diff(y)
                    ax = np.diff(vx); ay = np.diff(vy)
                    return [np.mean(x), np.std(x), np.mean(y), np.std(y), 
                            np.mean(vx), np.std(vx), np.mean(vy), np.std(vy),
                            np.mean(ax), np.std(ax), np.mean(ay), np.std(ay)]
                behavior_all['X'].append(extract_kinematics(beh_data[t_idx, 0, 4093:4624], beh_data[t_idx, 1, 4093:4624]))
                behavior_all['y'].append(1)
                behavior_all['X'].append(extract_kinematics(beh_data[t_idx, 0, 3593:4093], beh_data[t_idx, 1, 3593:4093]))
                behavior_all['y'].append(0)

    # Aggregated Results
    output_dir = FIGURES_DIR / 'final_reports'
    os.makedirs(output_dir, exist_ok=True)
    df_res = pd.DataFrame(session_results)
    if not df_res.empty:
        summary = df_res.groupby('Area').agg({'Train': 'mean', 'Test': ['mean', 'sem']}).reset_index()
        summary.columns = ['Area', 'Train_Mean', 'Test_Mean', 'Test_SEM']
        
        # Plot Identity Decoding
        fig = go.Figure(data=[
            go.Bar(name='Train', x=summary['Area'], y=summary['Train_Mean'], marker_color='lightblue'),
            go.Bar(name='Test', x=summary['Area'], y=summary['Test_Mean'], 
                   error_y=dict(type='data', array=summary['Test_SEM']), marker_color='darkblue')
        ])
        fig.add_hline(y=0.33, line_dash="dash", annotation_text="Chance (33%)")
        fig.update_layout(title="Omission Identity Decoding (A vs B vs null-R, 50-50 Split)",
                          yaxis_title="Accuracy", template="plotly_white", barmode='group')
        fig.write_html(output_dir / "FIG_05A_Identity_Decoding.html")

    # Behavioral Result (50-50 Split)
    X_b = np.array(behavior_all['X'])
    y_b = np.array(behavior_all['y'])
    if len(y_b) > 20:
        X_tr, X_te, y_tr, y_te = train_test_split(X_b, y_b, test_size=0.50, random_state=None, shuffle=True, stratify=y_b)
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr); X_te = scaler.transform(X_te)
        clf_b = LogisticRegression().fit(X_tr, y_tr)
        beh_acc = accuracy_score(y_te, clf_b.predict(X_te))
        
        fig_b = go.Figure(data=[go.Bar(x=["Eye Kinematics"], y=[beh_acc], marker_color='gray')])
        fig_b.add_hline(y=0.50, line_dash="dash", annotation_text="Chance (50%)")
        fig_b.update_layout(title="Behavioral Decoding (Omission vs Delay, 50-50 Split)", yaxis_title="Accuracy", yaxis_range=[0,1])
        fig_b.write_html(output_dir / "FIG_05B_Behavioral_Control.html")


def main(args=None):
    decode_figure_5()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
