
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

# Timing windows
WINDOWS = {
    'p2': (2062, 2593),
    'p3': (3124, 3655),
    'p4': (4186, 4717),
}

def run_oddball_classification():
    units_df = pd.read_csv(os.path.join(CHECKPOINT_DIR, 'neuron_categories.csv'))
    all_results = []
    
    for sid in SESSIONS:
        print(f"Processing Session {sid}...")
        v1_units = units_df[(units_df['session'] == int(sid)) & (units_df['area'].str.contains('V1'))]
        if len(v1_units) == 0: continue
        probes = v1_units['probe'].unique()
        
        # Identity B: Stim 4 (AAAB) vs Stim 2/3 (BBBA)
        X_p4_b_list = []
        X_p23_b_list = []
        
        # Identity A: Stim 4 (BBBA) vs Stim 2/3 (AAAB)
        X_p4_a_list = []
        X_p23_a_list = []
        
        for p in probes:
            # Identity B
            f_aaab = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-AAAB.npy')
            f_bbba = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-BBBA.npy')
            
            if os.path.exists(f_aaab) and os.path.exists(f_bbba):
                unit_indices = v1_units[v1_units['probe'] == p]['unit_idx'].values
                
                # B at P4 (AAAB)
                data_p4_b = np.load(f_aaab, mmap_mode='r')[:, unit_indices, WINDOWS['p4'][0]:WINDOWS['p4'][1]]
                X_p4_b_list.append(np.mean(data_p4_b, axis=2))
                
                # B at P2 and P3 (BBBA)
                data_p2_b = np.load(f_bbba, mmap_mode='r')[:, unit_indices, WINDOWS['p2'][0]:WINDOWS['p2'][1]]
                data_p3_b = np.load(f_bbba, mmap_mode='r')[:, unit_indices, WINDOWS['p3'][0]:WINDOWS['p3'][1]]
                X_p23_b_list.append(np.mean(np.concatenate([data_p2_b, data_p3_b], axis=0), axis=2))

                # A at P4 (BBBA)
                data_p4_a = np.load(f_bbba, mmap_mode='r')[:, unit_indices, WINDOWS['p4'][0]:WINDOWS['p4'][1]]
                X_p4_a_list.append(np.mean(data_p4_a, axis=2))
                
                # A at P2 and P3 (AAAB)
                data_p2_a = np.load(f_aaab, mmap_mode='r')[:, unit_indices, WINDOWS['p2'][0]:WINDOWS['p2'][1]]
                data_p3_a = np.load(f_aaab, mmap_mode='r')[:, unit_indices, WINDOWS['p3'][0]:WINDOWS['p3'][1]]
                X_p23_a_list.append(np.mean(np.concatenate([data_p2_a, data_p3_a], axis=0), axis=2))

        # Run Classifiers
        for identity, X_p4_list, X_p23_list in [('Identity B', X_p4_b_list, X_p23_b_list), ('Identity A', X_p4_a_list, X_p23_a_list)]:
            if X_p4_list and X_p23_list:
                X_p4 = np.hstack(X_p4_list)
                X_p23 = np.hstack(X_p23_list)
                
                n_min = min(len(X_p4), len(X_p23))
                if n_min > 5:
                    idx_p4 = np.random.choice(len(X_p4), n_min, replace=False)
                    idx_p23 = np.random.choice(len(X_p23), n_min, replace=False)
                    X_bal = np.vstack([X_p4[idx_p4], X_p23[idx_p23]])
                    y_bal = np.concatenate([np.zeros(n_min), np.ones(n_min)])
                    
                    shuffle_idx = np.random.permutation(len(y_bal))
                    X_bal = X_bal[shuffle_idx]
                    y_bal = y_bal[shuffle_idx]
                    
                    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                    clf = SVC(kernel='linear')
                    scores = cross_val_score(clf, X_bal, y_bal, cv=skf, scoring='accuracy')
                    
                    all_results.append({
                        'session': sid,
                        'identity': identity,
                        'accuracy': np.mean(scores)
                    })

    df = pd.DataFrame(all_results)
    if df.empty: return
    
    summary = df.groupby('identity')['accuracy'].agg(['mean', 'std']).reset_index()
    print("\nOddball Decoding Summary (P4 vs P2/P3):")
    print(summary)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary['identity'],
        y=summary['mean'],
        error_y=dict(type='data', array=summary['std']),
        name='Oddball (P4) vs Repeated (P2/P3)'
    ))
    fig.add_hline(y=0.5, line_dash="dot", line_color="gray", annotation_text="Chance")
    fig.update_layout(title="Figure 04: Oddball vs Repeated Identity Decoding (V1 Pop)",
                      yaxis_title="Accuracy (50/50 Balanced)", template="plotly_white")
    
    fig.write_html(os.path.join(OUTPUT_DIR, "FIG_04_Oddball_Decoding.html"))
    print("Saved FIG_04.")

if __name__ == '__main__':
    run_oddball_classification()
