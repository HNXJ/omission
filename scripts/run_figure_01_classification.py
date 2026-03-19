
import numpy as np
import pandas as pd
import os
import glob
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
import plotly.graph_objects as go

# Parameters
SESSIONS = ['230629', '230630', '230714', '230719', '230720', '230721', '230816', '230818', '230823', '230825', '230830', '230831', '230901']
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Omission Groups: (Conditions, Omit Win, Preceding Delay Win)
OMIT_GROUPS = {
    'P4 Omission': (['AAAX', 'RRRX', 'BBBX'], (4186, 4717), (3655, 4186)),
    'P3 Omission': (['AAXB', 'RRXR', 'BBXA'], (3124, 3655), (2593, 3124)),
    'P2 Omission': (['AXAB', 'RXRR', 'BXBA'], (2062, 2593), (1531, 2062)),
}

def load_pupil(sid, cond):
    fpath = os.path.join(DATA_DIR, f'ses{sid}-behavioral-{cond}.npy')
    if not os.path.exists(fpath): return None
    data = np.load(fpath, mmap_mode='r')
    return data[:, 0, :] # (trials, 6000)

def run_pupil_omission_detection():
    all_results = []
    
    for sid in SESSIONS:
        print(f"Processing Session {sid}...")
        
        for group_name, (conds, omit_win, delay_win) in OMIT_GROUPS.items():
            omit_data_list = []
            delay_data_list = []
            
            for cond in conds:
                pupil = load_pupil(sid, cond)
                if pupil is not None:
                    # Feature: Mean pupil diameter in window
                    omit_data_list.append(np.mean(pupil[:, omit_win[0]:omit_win[1]], axis=1).reshape(-1, 1))
                    delay_data_list.append(np.mean(pupil[:, delay_win[0]:delay_win[1]], axis=1).reshape(-1, 1))
            
            if omit_data_list:
                X_omit = np.vstack(omit_data_list)
                X_delay = np.vstack(delay_data_list)
                
                # Balanced Validation
                n_min = min(len(X_omit), len(X_delay))
                if n_min > 5:
                    idx_o = np.random.choice(len(X_omit), n_min, replace=False)
                    idx_d = np.random.choice(len(X_delay), n_min, replace=False)
                    X_bal = np.vstack([X_omit[idx_o], X_delay[idx_d]])
                    y_bal = np.concatenate([np.ones(n_min), np.zeros(n_min)]) # Omit=1, Delay=0
                    
                    shuffle_idx = np.random.permutation(len(y_bal))
                    X_bal = X_bal[shuffle_idx]
                    y_bal = y_bal[shuffle_idx]
                    
                    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                    clf = SVC(kernel='linear')
                    scores = cross_val_score(clf, X_bal, y_bal, cv=skf, scoring='accuracy')
                    
                    all_results.append({
                        'session': sid,
                        'group': group_name,
                        'accuracy': np.mean(scores)
                    })

    df = pd.DataFrame(all_results)
    if df.empty: return
    
    summary = df.groupby('group')['accuracy'].agg(['mean', 'std']).reset_index()
    print("\nPupil Omission Detection Performance (vs. preceding delay):")
    print(summary)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary['group'],
        y=summary['mean'],
        error_y=dict(type='data', array=summary['std']),
        name='Within-Trial Pupil Detection'
    ))
    fig.add_hline(y=0.5, line_dash="dot", line_color="gray", annotation_text="Chance")
    fig.update_layout(title="Figure 01: Pupil-Based Omission Detection (Gray Window vs. Previous Gray Delay)",
                      yaxis_title="Accuracy (50/50 Balanced)", template="plotly_white")
    
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_01_Pupil_Omission_Detection.html"))
    print("Saved FIG_01.")

if __name__ == '__main__':
    run_pupil_omission_detection()
