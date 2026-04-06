from codes.config.paths import BEHAVIORAL_DIR, FIGURES_DIR

import numpy as np
import pandas as pd
import scipy.io as sio
import os
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# New color palette
COLORS = ['red', 'blue', 'green', 'yellow', 'brown', 'pink', 'gray', 'purple', 'cyan', 'darkblue', 'darkred', 'darkgreen', 'darkyellow', 'black']
BAND_COLORS = {'Theta': 'purple', 'Alpha': 'orange', 'Beta': 'red', 'Gamma': 'blue'}

# Task Timing (Relative to P1 Onset at Sample 1000)
OMISSION_CONFIGS = {
    'p2': {'start': 531, 'end': 2062},
    'p3': {'start': 1562, 'end': 3093},
    'p4': {'start': 2593, 'end': 4124}
}

CONDITION_MAP = {
    1: 'AAAB', 2: 'AAAB',
    3: 'AXAB',
    4: 'AAXB',
    5: 'AAAX',
    6: 'BBBA', 7: 'BBBA',
    8: 'BXBA',
    9: 'BBXA',
    10: 'BBBX',
    **{i: 'RRRR' for i in range(11, 27)},
    **{i: 'RXRR' for i in range(27, 35)},
    35: 'RRXR', 37: 'RRXR', 39: 'RRXR', 41: 'RRXR',
    36: 'RRRX', 38: 'RRRX', 40: 'RRRX', 42: 'RRRX',
    **{i: 'RRRX' for i in range(43, 51)},
}

def identify_condition_from_number(condition_number):
    """Maps a condition number to its string name."""
    return CONDITION_MAP.get(condition_number, f"Unknown_Cond_{condition_number}")

def parse_bhv_eye_data(mat_path):
    """Direct parsing of .mat BHV file for eye DVA with condition grouping."""
    print(f"DEBUG: Parsing {mat_path}")
    try:
        mat = sio.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
        bhvUni = mat['bhvUni']
        results = {} # condition -> list of eye windows
        
        for i, trial in enumerate(bhvUni):
            if trial.TrialError != 0:
                continue
            
            cond_name = identify_condition_from_number(trial.Condition)
            if 'X' not in cond_name: # Only omissions
                continue
            
            codes = trial.BehavioralCodes.CodeNumbers
            times = trial.BehavioralCodes.CodeTimes
            p1_idx = np.where(codes == 101)[0]
            if len(p1_idx) == 0:
                continue
            p1_time = times[p1_idx[0]]
            
            eye = trial.AnalogData.Eye # (nSamples, 2)
            
            # Determine which omission it is (p2, p3, or p4)
            omit_label = 'p' + str(cond_name.find('X') + 1)
            if omit_label not in OMISSION_CONFIGS:
                continue
            
            config = OMISSION_CONFIGS[omit_label]
            start_ms = int(p1_time + config['start'])
            end_ms = int(p1_time + config['end'])
            
            if end_ms < len(eye):
                win = eye[start_ms:end_ms, :]
                if cond_name not in results: results[cond_name] = []
                results[cond_name].append(win)
                    
        print(f"DEBUG: parse_bhv_eye_data for {os.path.basename(mat_path)} returning {len(results)} conditions.")
        return results
    except Exception as e:
        print(f"DEBUG: Error parsing {mat_path}: {e}")
        return None

def process_batch():
    bhv_dir = str(BEHAVIORAL_DIR)
    output_dir = str(FIGURES_DIR / 'part01')
    os.makedirs(output_dir, exist_ok=True)
    
    bhv_paths = glob.glob(os.path.join(bhv_dir, "*.mat"))
    sessions = sorted(list(set([os.path.basename(p).split('_')[0] for p in bhv_paths])))

    for sid in sessions:
        print(f"--- Processing Session: {sid} ---")
        
        bhv_file = glob.glob(os.path.join(bhv_dir, f"{sid}*.mat"))
        if not bhv_file:
            print(f"ERROR: No .mat file found for session {sid}")
            continue

        print(f"Found bhv file: {bhv_file[0]}")
        eye_data = parse_bhv_eye_data(bhv_file[0])

        if not eye_data:
            print("ERROR: No eye data parsed.")
            continue

        print(f"Parsed {len(eye_data)} conditions with eye data.")
        for cond_name, group in eye_data.items():
            print(f"  - Condition {cond_name}: {len(group)} trials")
            group_arr = np.array(group)
            mu = np.mean(group_arr, axis=0)
            sem = np.std(group_arr, axis=0) / np.sqrt(len(group))
            time = np.arange(mu.shape[0]) - 531
            
            fig = go.Figure()
            # X
            fig.add_trace(go.Scatter(x=time, y=mu[:, 0] + sem[:, 0], line_width=0, showlegend=False))
            fig.add_trace(go.Scatter(x=time, y=mu[:, 0] - sem[:, 0], fill='tonexty', fillcolor='red', opacity=0.2, line_width=0, showlegend=False))
            fig.add_trace(go.Scatter(x=time, y=mu[:, 0], name='Avg X', line=dict(color='red', width=3)))
            # Y
            fig.add_trace(go.Scatter(x=time, y=mu[:, 1] + sem[:, 1], line_width=0, showlegend=False))
            fig.add_trace(go.Scatter(x=time, y=mu[:, 1] - sem[:, 1], fill='tonexty', fillcolor='blue', opacity=0.2, line_width=0, showlegend=False))
            fig.add_trace(go.Scatter(x=time, y=mu[:, 1], name='Avg Y', line=dict(color='blue', width=3)))
            
            fig.add_vline(x=0, line_dash="dash", line_color="black", annotation_text="Onset")
            fig.add_vline(x=500, line_dash="dash", line_color="black", annotation_text="Offset")
            fig.update_layout(title=f"Eye DVA: {sid} {cond_name}", template="plotly_white")
            out_path = os.path.join(output_dir, f"EYE_DVA_{sid}_{cond_name}.html")
            fig.write_html(out_path)
            print(f"    -> Saved {out_path}")


def main(args=None):
    process_batch()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
