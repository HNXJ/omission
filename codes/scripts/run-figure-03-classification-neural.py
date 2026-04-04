
import numpy as np
import pandas as pd
import os
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
import plotly.graph_objects as go

# Parameters
SESSIONS = ['230630', '230816', '230830']
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
CHECKPOINT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\final_reports'

OMIT_GROUPS = {
    'P4 Omission': (['AAAX', 'RRRX', 'BBBX'], (4186, 4717), (3655, 4186)),
    'P3 Omission': (['AAXB', 'RRXR', 'BBXA'], (3124, 3655), (2593, 3124)),
    'P2 Omission': (['AXAB', 'RXRR', 'BXBA'], (2062, 2593), (1531, 2062)),
}

def run_neural_omission_detection():
    units_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    all_results = []
    
    for sid in SESSIONS:
        print(f"Processing Session {sid}...")
        
        # 1. Identity Decoding (A vs B) at P4
        v1_units = units_df[(units_df['session'] == int(sid)) & (units_df['area'].str.contains('V1'))]
        if not v1_units.empty:
            for task_name, cond_a, cond_b in [('Identity A vs B', 'AAAB', 'BBBA')]:
                feat_a, feat_b = [], []
                probes = v1_units['probe'].unique()
                
                # Check if all probes have both conditions
                valid = True
                for p in probes:
                    if not (os.path.exists(os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond_a}.npy')) and 
                            os.path.exists(os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond_b}.npy'))):
                        valid = False; break
                
                if valid:
                    probe_a_data, probe_b_data = [], []
                    for p in probes:
                        u_idx = v1_units[v1_units['probe'] == p]['unit_idx'].values
                        probe_a_data.append(np.mean(np.load(os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond_a}.npy'), mmap_mode='r')[:, u_idx, 4186:4717], axis=2))
                        probe_b_data.append(np.mean(np.load(os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond_b}.npy'), mmap_mode='r')[:, u_idx, 4186:4717], axis=2))
                    
                    X_a = np.hstack(probe_a_data)
                    X_b = np.hstack(probe_b_data)
                    n_min = min(len(X_a), len(X_b))
                    if n_min > 5:
                        X_bal = np.vstack([X_a[np.random.choice(len(X_a), n_min, replace=False)], X_b[np.random.choice(len(X_b), n_min, replace=False)]])
                        y_bal = np.concatenate([np.zeros(n_min), np.ones(n_min)])
                        shuffle_idx = np.random.permutation(len(y_bal))
                        scores = cross_val_score(SVC(kernel='linear'), X_bal[shuffle_idx], y_bal[shuffle_idx], cv=5)
                        all_results.append({'session': sid, 'task': task_name, 'area': 'V1', 'accuracy': np.mean(scores)})

        # 2. Omission Detection (Within-Trial)
        oxm_units = units_df[(units_df['session'] == int(sid)) & (units_df['category'] == 'oxm+')]
        if not oxm_units.empty:
            probes = oxm_units['probe'].unique()
            for group_name, (conds, omit_win, delay_win) in OMIT_GROUPS.items():
                X_omit_trials = []
                X_delay_trials = []
                
                for cond in conds:
                    cond_probe_data_omit = []
                    cond_probe_data_delay = []
                    valid_cond = True
                    for p in probes:
                        f = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond}.npy')
                        if os.path.exists(f):
                            u_idx = oxm_units[oxm_units['probe'] == p]['unit_idx'].values
                            data = np.load(f, mmap_mode='r')
                            cond_probe_data_omit.append(np.mean(data[:, u_idx, omit_win[0]:omit_win[1]], axis=2))
                            cond_probe_data_delay.append(np.mean(data[:, u_idx, delay_win[0]:delay_win[1]], axis=2))
                        else:
                            valid_cond = False; break
                    
                    if valid_cond and cond_probe_data_omit:
                        X_omit_trials.append(np.hstack(cond_probe_data_omit))
                        X_delay_trials.append(np.hstack(cond_probe_data_delay))
                
                if X_omit_trials:
                    X_omit = np.vstack(X_omit_trials)
                    X_delay = np.vstack(X_delay_trials)
                    n_min = min(len(X_omit), len(X_delay))
                    if n_min > 5:
                        X_bal = np.vstack([X_omit[np.random.choice(len(X_omit), n_min, replace=False)], X_delay[np.random.choice(len(X_delay), n_min, replace=False)]])
                        y_bal = np.concatenate([np.ones(n_min), np.zeros(n_min)])
                        shuffle_idx = np.random.permutation(len(y_bal))
                        scores = cross_val_score(SVC(kernel='linear'), X_bal[shuffle_idx], y_bal[shuffle_idx], cv=5)
                        all_results.append({'session': sid, 'task': f'Omit Detect ({group_name})', 'area': 'oxm+', 'accuracy': np.mean(scores)})

    df = pd.DataFrame(all_results)
    if df.empty: return
    summary = df.groupby(['task', 'area'])['accuracy'].agg(['mean', 'std']).reset_index()
    print("\nNeural Classification Summary (Within-Trial):")
    print(summary)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary['task'], y=summary['mean'], error_y=dict(type='data', array=summary['std']), marker_color='purple'))
    fig.add_hline(y=0.5, line_dash="dot", line_color="gray", annotation_text="Chance")
    fig.update_layout(title="Figure 03: Neural Decoding of Identity (A/B) and Omission (Omit vs Delay)",
                      yaxis_title="Accuracy (50/50 Balanced)", template="plotly_white")
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_03_Neural_Decoding.html"))
    print("Saved FIG_03.")

if __name__ == '__main__':
    run_neural_omission_detection()
